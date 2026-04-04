from __future__ import annotations

import asyncio
import tempfile
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI, File, UploadFile
from openai import AsyncOpenAI
from pydantic import BaseModel

from app.embed import EMBED_MODEL, _get_collection, embed_file

# API-Key aus der .env-Datei im gleichen Ordner laden
load_dotenv(Path(__file__).resolve().parent / ".env", override=True)

app = FastAPI()

# OpenAI-Client einmalig erstellen und für alle Requests teilen
openai_client = AsyncOpenAI()


# --- Pydantic-Modelle ---


class QueryRequest(BaseModel):
    query: str
    n_results: int = 5
    filter: dict[str, str] | None = None


class QueryResultItem(BaseModel):
    text: str
    metadata: dict[str, str]
    distance: float


class QueryResponse(BaseModel):
    results: list[QueryResultItem]


class IndexResponse(BaseModel):
    chunks_indexed: int


class HealthResponse(BaseModel):
    status: str
    chunks: int


# --- Endpunkte ---


@app.get("/health", response_model=HealthResponse)
async def health() -> HealthResponse:
    collection = _get_collection()
    return HealthResponse(status="ok", chunks=collection.count())


@app.post("/query", response_model=QueryResponse)
async def query(request: QueryRequest) -> QueryResponse:
    # Query-Text in Embedding umwandeln
    response = await openai_client.embeddings.create(
        model=EMBED_MODEL, input=request.query
    )
    query_embedding = response.data[0].embedding

    # where={} wirft Chroma-Fehler → Guard nötig
    where = request.filter if request.filter else None

    collection = _get_collection()
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=request.n_results,
        where=where,
    )

    # Chroma gibt Listen-von-Listen zurück; [0] = erste (einzige) Query
    items = [
        QueryResultItem(text=doc, metadata=meta, distance=dist)
        for doc, meta, dist in zip(
            # Verbindung der Daten
            results["documents"][0],
            results["metadatas"][0],
            results["distances"][0],
        )
    ]
    return QueryResponse(results=items)


@app.post("/index", response_model=IndexResponse)
async def index(file: UploadFile = File(...)) -> IndexResponse:
    # embed_file erwartet einen Dateipfad, kein Buffer → temporäre Datei anlegen
    contents = await file.read()
    with tempfile.NamedTemporaryFile(suffix=".aasx", delete=False) as tmp:
        tmp.write(contents)
        tmp_path = Path(tmp.name)
    try:
        # embed_file ist synchron → in Thread-Pool auslagern
        count = await asyncio.to_thread(embed_file, tmp_path)
    finally:
        tmp_path.unlink(missing_ok=True)
    return IndexResponse(chunks_indexed=count)
