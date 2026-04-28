# AASX Knowledge Base — Frontend

Nuxt 3 frontend for the AASX Knowledge Base. Proxies all `/api/**` requests to the FastAPI backend at `http://localhost:8000`.

## Pages

| Route | Description |
|-------|-------------|
| `/` | Semantic search — raw chunk results with similarity distances |
| `/chat` | RAG chat — ask questions in natural language, answered by `gpt-4o-mini` with source chunks |
| `/upload` | Upload and index `.aasx` files into the local Chroma vector store |

## Setup

```bash
npm install
```

## Development

Make sure the backend is running first (`uvicorn app.main:app --reload`), then:

```bash
npm run dev
# available at http://localhost:3000
```

## Build

```bash
npm run build
npm run preview
```
