# InnovaFund — Research Funding & Innovation Intelligence Platform

**Infosys Springboard Virtual Internship · Team 3**
Mentor: Ms. Reshma Gollapalli

> **Deliverable branch:** `final-integration` — this branch holds the complete,
> integrated project. `main` is kept as a pointer README only.

## Where the code is

## Overview

Researchers, startups, universities and innovation centers track funding calls,
publication trends, patent activity and commercialization pathways across dozens of
disconnected portals. InnovaFund brings them into one platform: it discovers relevant
funding, analyses research and technology trends, maps the patent landscape, scores
innovation potential and suggests commercialization routes — through role-based
dashboards.

---

## Team

| Member | Module |
|---|---|
| Navya | Authentication, roles & research profiles |
| Mayank | Grant matching & technology intelligence, executive analytics |
| Kesiya Sunny | Patent landscape analysis & recommendations |
| Venkatesh Kulkarni | Innovation scoring engine, branch integration |
| Kanishka | Platform APIs, commercialization & dashboards |
| Anuhya Kurakula | Research trend intelligence, dataset services |
| Saumyaa | Testing, QA & milestone reporting |
| Nithya | Documentation & review support |

---

## Repository layout

```
backend/                     FastAPI application (main.py) — routers, services, models
innovation-scoring-service/  Innovation scoring microservice (also embedded in the API)
frontend/                    React 19 + Vite single-page application
backend/data/                Funding opportunities dataset (5,000 rows)
backend/lens-export.csv      Lens.org patent dataset (10,000 patents, 37 attributes)
docs/                        Architecture, database and API documentation
```

---

## Tech stack

- **Frontend:** React 19 · Vite · React Router · axios
- **Backend:** Python · FastAPI · Uvicorn · Pydantic · SQLAlchemy · Alembic
- **Intelligence:** scikit-learn (TF-IDF, cosine similarity) · pandas · rule and
  weighted-scoring engines
- **Databases:** PostgreSQL (primary) · SQLite (automatic fallback) · MongoDB (optional)
- **Auth:** JWT (python-jose) · bcrypt · Google OAuth
- **DevOps & testing:** Docker · Docker Compose · pytest

---

## Running the project

**Backend** (from the `backend` folder):

```bash
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

The API is then available at `http://127.0.0.1:8000/api`, with interactive docs at
`http://127.0.0.1:8000/docs`. If PostgreSQL is not running, the backend falls back to
SQLite automatically.

**Seed the datasets** (run these *after* the backend has started once, so the tables
exist):

```bash
python load_funding_csv.py    # funding opportunities
python seed_patents.py        # 10,000 Lens.org patents
```

**Frontend** (from the `frontend` folder):

```bash
npm install
npm run dev
```

The app runs at `http://localhost:5173` and calls the backend at
`http://127.0.0.1:8000/api`.

---

## Modules and APIs

| Module | Endpoints | Status |
|---|---|---|
| Authentication & roles | `/api/auth` | Completed |
| Research profiles | `/api/profiles` | Completed |
| Admin (users, audit logs, metrics) | `/api/admin` | Completed |
| Dataset services (OpenAlex, CrossRef, Semantic Scholar) | `/api/datasets` | Integrated |
| Funding recommendations | `/api/recommendations` | Completed |
| Grant matching & eligibility | `/api/grants` | Completed |
| Patent landscape analysis | `/api/patents` | Completed |
| Technology intelligence | `/api/technology` | Completed |
| Innovation scoring | `/api/scoring` | Completed |
| Research trends | `/api/trends` | Integrated |
| Commercialization recommendations | `/api/commercialization` | In progress |
| Reports, exports and alerts | — | Future scope |

### Scoring logic

- **Funding recommendation:** TF-IDF + cosine domain fit (60%), past success rate (20%),
  deadline window (10%), log-scaled amount (10%), clamped to 0–1 and reported as 0–100
  with reasoning.
- **Patent strength:** 0.6 × citation impact + 0.4 × recency (patents older than 20 years
  score 0 on recency).
- **Innovation score:** weighted five-pillar model — research novelty 30%, patent strength
  20%, market potential 20%, technology maturity 15%, funding relevance 15% — mapped to
  bands from Very Low to Very High.

---

## Verified status

- Backend boots and serves **70 routes** with no server errors on any GET endpoint
- Register and login return 200; scoring, trends, technology, patents and
  commercialization endpoints all return 200
- Seeding loads **10,000 patents**, producing 10 technology clusters and 168
  year × domain trend points
- Frontend production build succeeds
- Test suites: innovation scoring (27), grant matching and technology intelligence (11),
  recommendation engine (7), patent analysis (5)

---

## Integration

All nine member branches were merged into this branch through pull requests #2–#5,
including restoring a previously reverted merge and resolving conflicts across
`main.py`, `models.py`, `schemas.py`, `requirements.txt` and the frontend routing files.
Please create new branches from `final-integration`, not from `main`.
