# AASX Knowledge Base

Semantic search over AASX files (Asset Administration Shell). Upload `.aasx` files, and they get automatically parsed into searchable chunks, embedded via OpenAI, and stored in a local vector database. You can then search in plain language through a web interface.

---

## What is this?

[AASX](https://www.ipa.fraunhofer.de/de/aktuelle-forschung/kompetenzzentrum-digitale-werkzeuge-in-der-produktion/digital-twin/asset-administration-shell.html) is a file format for digitally describing industrial assets and components (e.g. machines, sensors, parts). This app makes those files searchable — you can ask things like *"What is the serial number of the device?"* or *"What is the rated voltage?"*

**How it works:**

```
.aasx file → Parse → Chunks → OpenAI Embeddings → Chroma (local)
                                                        ↓
                                        Nuxt 3 Frontend → FastAPI → Search / Chat result
```

---

## Requirements

- Python 3.11+
- Node.js 18+
- OpenAI API key

---

## Setup

### 1. Set up the Python environment

```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configure the API key

```bash
# Create the .env file inside the app/ directory:
echo "OPENAI_API_KEY=sk-..." > app/.env
```

### 3. Install frontend dependencies

```bash
cd frontend
npm install
```

---

## Running the app

Both backend and frontend need to be running at the same time.

**Backend** (Terminal 1):
```bash
uvicorn app.main:app --reload
# available at http://localhost:8000
```

**Frontend** (Terminal 2):
```bash
cd frontend
npm run dev
# available at http://localhost:3000
```

Then open [http://localhost:3000](http://localhost:3000) in your browser.

---

## Indexing an AASX file

**Option A – Web interface:**
Go to *Indexieren*, and upload an `.aasx` file.

**Option B – Command line:**
```bash
python -m app.embed my-file.aasx
```

---

## API

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/health` | Status and number of indexed chunks |
| `POST` | `/query` | Semantic search — returns raw chunks with distances |
| `POST` | `/chat` | RAG chat — returns an LLM answer with sources |
| `POST` | `/index` | Upload and index an AASX file |

**Example query:**
```bash
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{"query": "serial number", "n_results": 3}'
```

**Example chat:**
```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Wie hoch ist die Temperatur?", "n_results": 5}'
```

---

## Project structure

```
.
├── app/
│   ├── parse.py        # AASX → list of AASChunks (via BaSyx SDK)
│   ├── embed.py        # Chunks → OpenAI Embeddings → Chroma
│   └── main.py         # FastAPI: /health, /query, /chat, /index
├── frontend/
│   └── app/
│       ├── app.vue         # Layout + health badge + navigation
│       └── pages/
│           ├── index.vue   # Semantic search interface
│           ├── chat.vue    # RAG chat interface
│           └── upload.vue  # File upload / indexing
├── chroma_data/        # local vector store (created automatically)
└── requirements.txt
```

---

## Development

```bash
# Run tests
pytest -v --tb=short

# Lint & type check
ruff check . && mypy app/

# Format
ruff format .
```

---

## Stack

| Component | Technology |
|-----------|------------|
| Backend | FastAPI + Python 3.11 |
| Parsing | BaSyx Python SDK |
| Embeddings | OpenAI `text-embedding-3-small` |
| Vector store | Chroma (local, persistent) |
| Frontend | Nuxt 3 + Tailwind CSS |
