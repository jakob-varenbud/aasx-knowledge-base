from __future__ import annotations

from pathlib import Path

from basyx.aas import model
from basyx.aas.adapter import aasx
from basyx.aas.util.traversal import walk_submodel
from pydantic import BaseModel


# Ein Chunk repräsentiert genau ein SubmodelElement als Einheit für die Vektorisierung.
# 'text' ist der für das LLM lesbare Inhalt; 'metadata' enthält strukturierte
# Felder für späteres Filtern in Chroma (z.B. nach asset_id oder semantic_id).
class AASChunk(BaseModel):
    text: str
    metadata: dict


def _build_path(element: model.SubmodelElement) -> str:
    """Baut einen lesbaren Pfad zum Element innerhalb seines Submodels.

    Wandert über .parent-Referenzen nach oben, bis das Submodel erreicht wird,
    und verbindet die id_shorts mit '/'. Beispiel: "NameplateData/ManufacturerName"
    """
    parts: list[str] = []
    node: model.Referable | None = element
    while node is not None and not isinstance(node, model.Submodel):
        parts.append(node.id_short)
        node = node.parent  # type: ignore[assignment]
    return "/".join(reversed(parts))


def _extract_semantic_id(element: model.SubmodelElement) -> str | None:
    """Gibt die semantische ID des Elements zurück (erster Key-Wert).

    SemanticIDs verweisen auf standardisierte Konzepte (z.B. ECLASS, IEC CDD).
    Sie werden als Metadata gespeichert – nie in den Embedding-Text eingebettet,
    damit die semantische Bedeutung für strukturierte Abfragen erhalten bleibt.
    """
    if element.semantic_id is None:
        return None
    keys = element.semantic_id.key
    if keys:
        return str(keys[0].value)
    return None


def _element_to_text(
    element: model.SubmodelElement, submodel_id_short: str | None = None
) -> str:
    """Erzeugt einen menschenlesbaren Text für ein SubmodelElement.

    Struktur:
      "[Submodel: <submodel_id_short> / <element_path>]"
      "<idShort>: <Wert> (<Beschreibung>)"

    Der Breadcrumb-Header gibt dem Embedding den hierarchischen Kontext,
    damit isolierte Chunks wie "ManufacturerName: Siemens" im Retrieval
    korrekt verortet werden können.
    """
    path = _build_path(element)
    if submodel_id_short:
        header = f"[Submodel: {submodel_id_short} / {path}]"
    else:
        header = f"[{path}]"

    parts: list[str] = [element.id_short]

    if isinstance(element, model.Property):
        if element.value is not None:
            parts.append(f": {element.value}")
    elif isinstance(element, model.MultiLanguageProperty):
        if element.value:
            text = element.value.get("en") or next(iter(element.value.values()), None)
            if text:
                parts.append(f": {text}")
    elif isinstance(element, model.Range):
        parts.append(f": {element.min} … {element.max}")
    elif isinstance(element, model.File):
        if element.value:
            parts.append(f": {element.value}")
    elif isinstance(element, model.Blob):
        parts.append(f": <blob {element.content_type}>")

    if element.description:
        desc = element.description.get("en") or next(
            iter(element.description.values()), None
        )
        if desc:
            parts.append(f" ({desc})")

    return f"{header}\n{''.join(parts)}"


def parse_aasx(file_path: str | Path) -> list[AASChunk]:
    """Liest eine .aasx-Datei und gibt alle SubmodelElemente als Chunks zurück.

    Ablauf:
    1. AASX-Archiv öffnen und alle AAS-Objekte in einen DictObjectStore laden.
       (DictSupplementaryFileContainer nimmt eingebettete Dateien auf, wird hier
       aber nicht weiterverwendet – notwendig für die BaSyx-API.)
    2. asset_id aus der AssetAdministrationShell auslesen – sie identifiziert
       das physische Asset und wird jedem Chunk als Metadatum mitgegeben.
    3. Über alle Submodels iterieren und mit walk_submodel() jeden einzelnen
       SubmodelElement-Knoten besuchen (rekursiv, auch in SubmodelElementCollections).
    4. Pro Element einen AASChunk mit Text und Metadaten erzeugen.
    """
    object_store: model.DictObjectStore = model.DictObjectStore()
    file_store = aasx.DictSupplementaryFileContainer()

    with aasx.AASXReader(str(file_path)) as reader:
        reader.read_into(object_store=object_store, file_store=file_store)

    # asset_id aus der ersten gefundenen AssetAdministrationShell auslesen
    asset_id: str | None = None
    for item in object_store:
        if isinstance(item, model.AssetAdministrationShell):
            asset_id = str(item.id)
            break

    chunks: list[AASChunk] = []

    for submodel in object_store:
        if not isinstance(submodel, model.Submodel):
            continue

        submodel_id_short = submodel.id_short

        # walk_submodel liefert alle SubmodelElemente flach (depth-first),
        # einschließlich verschachtelter Elemente in Collections/Lists.
        for element in walk_submodel(submodel):
            chunk = AASChunk(
                text=_element_to_text(
                    element, submodel_id_short
                ),  # _build_path  wird in _element_to_text aufgerufen!
                metadata={
                    "asset_id": asset_id,
                    "submodel_id_short": submodel_id_short,
                    "semantic_id": _extract_semantic_id(element),
                    "element_path": _build_path(element),
                },
            )
            chunks.append(chunk)

    return chunks


if __name__ == "__main__":
    import json
    import sys

    chunks = parse_aasx(sys.argv[1])
    for c in chunks:
        print(json.dumps({"text": c.text, "metadata": c.metadata}, ensure_ascii=False))
