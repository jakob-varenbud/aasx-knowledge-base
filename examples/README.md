# Example AASX files

This folder contains sample AASX files you can use to try out the indexing and query pipeline without having to bring your own data.

## `Cnc_1.aasx`

A demo Asset Administration Shell describing a fictitious CNC machine. Contains common submodels such as Nameplate, TechnicalData, and Documentation.

Derived from BaSyx Python SDK examples (Apache-2.0) and extended for richer semantic content.

### Try it out

```bash
# Index the file
python -m app.embed examples/Cnc_1.aasx

# Run the backend
uvicorn app.main:app --reload

# Query it
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{"query": "manufacturer name", "n_results": 3}'
```
