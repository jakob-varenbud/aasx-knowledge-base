from __future__ import annotations
from dotenv import load_dotenv

import hashlib
import os
from pathlib import Path

import chromadb
from openai import OpenAI

from app.parse import AASChunk, parse_aasx

# Name der Sammlung in der Chroma-Datenbank
COLLECTION_NAME = "aasx_knowledge"

# OpenAI-Modell das Texte in Zahlen (Embeddings) umwandelt
EMBED_MODEL = "text-embedding-3-small"

# Pfad zur lokalen Chroma-Datenbank (zwei Ebenen über dieser Datei und dann in dem Verzeichnis chroma_data)
CHROMA_PATH = Path(__file__).parent.parent / "chroma_data"

# API-Key aus der .env-Datei im gleichen Ordner laden
load_dotenv(Path(__file__).resolve().parent / ".env", override=True)


def _chunk_id(chunk: AASChunk) -> str:
    # Erzeugt eine eindeutige ID für jeden Chunk aus asset_id + element_path.
    # SHA-256 liefert immer einen gleich langen String – egal wie lang die Eingabe ist.
    # Gleicher Chunk → gleiche ID → Chroma überschreibt statt doppelt zu speichern.
    key = f"{chunk.metadata.get('asset_id')}::{chunk.metadata.get('submodel_id_short')}::{chunk.metadata.get('element_path')}"
    return hashlib.sha256(key.encode()).hexdigest()


def _get_collection() -> chromadb.Collection:
    # Öffnet die lokale Chroma-Datenbank (oder erstellt sie beim ersten Aufruf).
    # get_or_create: existiert die Collection schon → verwenden, sonst neu anlegen.
    client = chromadb.PersistentClient(path=str(CHROMA_PATH))
    return client.get_or_create_collection(COLLECTION_NAME)


def embed_file(file_path: str | Path, batch_size: int = 100) -> int:
    """Parse *file_path*, embed all chunks, upsert into Chroma. Returns chunk count."""

    # Schritt 1: .aasx-Datei parsen → Liste von Chunks
    chunks = parse_aasx(file_path)
    if not chunks:
        return 0

    # Schritt 2: Verbindungen zu OpenAI und Chroma aufbauen
    openai_client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])
    collection = _get_collection()

    # Schritt 3: Chunks in Gruppen aufteilen (OpenAI-API hat ein Limit pro Anfrage)
    for i in range(0, len(chunks), batch_size):
        batch = chunks[i : i + batch_size]

        # Nur die Texte aus den Chunks extrahieren
        texts = [c.text for c in batch]

        # Texte an OpenAI schicken → zurück kommt pro Text eine Liste von ~1500 Zahlen
        response = openai_client.embeddings.create(model=EMBED_MODEL, input=texts)
        embeddings = [item.embedding for item in response.data]

        # Alles in Chroma speichern:
        # - ids: eindeutige Kennung pro Chunk
        # - embeddings: die Zahlenvektoren für die Ähnlichkeitssuche
        # - documents: der Originaltext (für spätere Anzeige)
        # - metadatas: asset_id, submodel etc. für strukturierte Filterung
        # None-Werte werden zu "" – Chroma erlaubt kein None in Metadaten
        collection.upsert(
            ids=[_chunk_id(c) for c in batch],
            embeddings=embeddings,
            documents=texts,
            metadatas=[
                {k: (v if v is not None else "") for k, v in c.metadata.items()}
                for c in batch
            ],
        )

    return len(chunks)


if __name__ == "__main__":
    import sys

    count = embed_file(sys.argv[1])
    print(f"Embedded {count} chunks into collection '{COLLECTION_NAME}'.")
