# AASX Knowledge Base

Semantische Suche über AASX-Dateien (Asset Administration Shell). Lade `.aasx`-Dateien hoch, die werden automatisch in durchsuchbare Chunks zerlegt, via OpenAI eingebettet und in einer lokalen Vektordatenbank gespeichert. Über ein Web-Interface kannst du dann in natürlicher Sprache suchen.

---

## Was ist das?

[AASX](https://www.plattform-i40.de/IP/Redaktion/EN/Downloads/Publikation/Details-of-the-Asset-Administration-Shell-Part1.html) ist ein Dateiformat für die digitale Beschreibung von Industrieanlagen und -komponenten (z.B. Maschinen, Sensoren, Bauteile). Diese App macht solche Dateien durchsuchbar – du kannst z.B. fragen: *"Welche Seriennummer hat das Gerät?"* oder *"Was ist die Nennspannung?"*

**Wie es funktioniert:**

```
.aasx-Datei → Parsen → Chunks → OpenAI Embeddings → Chroma (lokal)
                                                          ↓
                                              Nuxt 3 Frontend → FastAPI → Suchergebnis
```

---

## Voraussetzungen

- Python 3.11+
- Node.js 18+
- OpenAI API Key

---

## Setup

### 1. Python-Umgebung einrichten

```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### 2. API-Key konfigurieren

```bash
cp app/.env.example app/.env     # falls vorhanden
# oder direkt erstellen:
echo "OPENAI_API_KEY=sk-..." > app/.env
```

### 3. Frontend-Dependencies installieren

```bash
cd frontend
npm install
```

---

## Starten

Backend und Frontend müssen beide laufen.

**Backend** (Terminal 1):
```bash
uvicorn app.main:app --reload
# läuft auf http://localhost:8000
```

**Frontend** (Terminal 2):
```bash
cd frontend
npm run dev
# läuft auf http://localhost:3000
```

Dann [http://localhost:3000](http://localhost:3000) im Browser öffnen.

---

## AASX-Datei indexieren

**Option A – Web-Interface:**
Gehe auf *Indexieren*, lade eine `.aasx`-Datei hoch.

**Option B – Kommandozeile:**
```bash
python -m app.embed meine-datei.aasx
```

---

## API

| Methode | Pfad | Beschreibung |
|--------|------|--------------|
| `GET` | `/health` | Status und Anzahl indexierter Chunks |
| `POST` | `/query` | Semantische Suche |
| `POST` | `/index` | AASX-Datei hochladen und indexieren |

**Beispiel-Query:**
```bash
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{"query": "Seriennummer", "n_results": 3}'
```

---

## Projektstruktur

```
.
├── app/
│   ├── parse.py        # AASX → AASChunk-Liste (via BaSyx SDK)
│   ├── embed.py        # Chunks → OpenAI Embeddings → Chroma
│   └── main.py         # FastAPI: /health, /query, /index
├── frontend/
│   └── app/
│       ├── app.vue         # Layout + Health-Badge
│       └── pages/
│           ├── index.vue   # Suchoberfläche
│           └── upload.vue  # Datei-Upload
├── chroma_data/        # lokale Vektordatenbank (wird automatisch erstellt)
└── requirements.txt
```

---

## Entwicklung

```bash
# Tests
pytest -v --tb=short

# Linting & Typen
ruff check . && mypy app/

# Formatierung
ruff format .
```

---

## Stack

| Komponente | Technologie |
|-----------|-------------|
| Backend | FastAPI + Python 3.11 |
| Parsing | BaSyx Python SDK |
| Embeddings | OpenAI `text-embedding-3-small` |
| Vektordatenbank | Chroma (lokal, persistent) |
| Frontend | Nuxt 3 + Tailwind CSS |
