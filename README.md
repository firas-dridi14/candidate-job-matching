# Candidate–Job Matching Tool

A small tool that matches candidates to job postings. For every job it computes a score from 0 to 100 for each candidate and returns the **top 3 candidates**. Built as a learning project, inspired by how job platforms for skilled trades work.

Available in two versions with the same logic:

- **C** (`matching.c`): command-line program
- **Python** (`matching.py`) + **REST API** (`api.py`, FastAPI)

> **Data protection:** only synthetic test data is used (no real people), in line with GDPR.

## How the score works

| Criterion | Points |
|---|---|
| Same occupation (otherwise score = 0) | 50 |
| Same city | 20 |
| Required skills the candidate has (proportional) | up to 20 |
| Enough years of experience | 10 |

## Files

| File | Purpose |
|---|---|
| `kandidaten.csv` | 20 fake candidates |
| `stellen.csv` | 8 fake job postings |
| `matching.c` | C version |
| `matching.py` | Python version (scoring logic) |
| `api.py` | REST API on top of `matching.py` |

## Run the C version

```bash
gcc -Wall -o matching matching.c
./matching          # Windows PowerShell: .\matching.exe
```

Prints the top 3 candidates per job and writes `ergebnis.csv`.

## Run the Python version and the API

```bash
pip install fastapi "uvicorn[standard]"
python matching.py                      # prints results, writes ergebnis.csv
python -m uvicorn api:app --reload      # starts the API
```

Open <http://127.0.0.1:8000/docs> to try it interactively.

| Endpoint | Description |
|---|---|
| `GET /` | Health check |
| `GET /stellen` | List all jobs |
| `GET /stellen/{stelle_id}/matches?anzahl=3` | Top candidates for a job (404 if the job does not exist) |

Example: `GET /stellen/103/matches` returns the best candidates for job 103 as JSON.

## Limitations and ideas

- Cities and skills must match exactly (no distance or synonym matching yet).
- Data comes from CSV files instead of a database.
- Ideas: weighted skills, distance between cities, a database (PostgreSQL), tests, multi-threaded processing of many jobs.