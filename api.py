"""
Matching-API: stellt das Matching ueber eine kleine Web-API bereit.
Nur Testdaten (keine echten Personen) - DSGVO-konform.

Starten:  python -m uvicorn api:app --reload
Testen:   http://127.0.0.1:8000/docs
"""
from fastapi import FastAPI, HTTPException

# Wir benutzen die Funktionen aus matching.py (gleicher Ordner)
from matching import lese_csv, beste_kandidaten

app = FastAPI(title="Werkia Matching API")

# Die Daten werden beim Start einmal aus den CSV-Dateien gelesen
kandidaten = lese_csv("kandidaten.csv")
stellen = lese_csv("stellen.csv")


@app.get("/")
def start():
    """Kleine Willkommensnachricht."""
    return {"message": "Matching-API laeuft", "docs": "/docs"}


@app.get("/stellen")
def alle_stellen():
    """Liste aller Stellen."""
    return stellen


@app.get("/stellen/{stelle_id}/matches")
def matches(stelle_id: int, anzahl: int = 3):
    """Die besten Kandidaten fuer eine Stelle (Standard: 3)."""
    stelle = next((s for s in stellen if int(s["id"]) == stelle_id), None)
    if stelle is None:
        raise HTTPException(status_code=404, detail="Stelle nicht gefunden")

    top = beste_kandidaten(stelle, kandidaten, anzahl)
    return {
        "stelle": {
            "id": int(stelle["id"]),
            "firma": stelle["firma"],
            "beruf": stelle["beruf"],
            "stadt": stelle["stadt"],
        },
        "matches": [
            {
                "platz": platz,
                "kandidat": k["name"],
                "stadt": k["stadt"],
                "erfahrung_jahre": int(k["erfahrung_jahre"]),
                "score": score,
            }
            for platz, (score, k) in enumerate(top, start=1)
        ],
    }