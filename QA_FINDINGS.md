\# Milestone 2 — QA Findings



Findings from running and reviewing branches during integration testing setup (Member 8 role). Documented here for the owning member to review/apply.



\## 1. Patent save fails on date fields (Anuhya-Kurakula branch)



\*\*Location:\*\* `backend/app/services/assets.py`, `save\_patent()`



\*\*Issue:\*\* `test\_patent\_search\_and\_save` fails with:



bson.errors.InvalidDocument: Invalid document: cannot encode object: datetime.date(2004, 10, 8), of type: <class 'datetime.date'>





\*\*Cause:\*\* `save\_patent()` converts `filing\_date` from a string to a Python `date` object for the Postgres model, but the same mutated `data` dict is then written to MongoDB via `data.get("raw", data)`. MongoDB's BSON encoder can't serialize a bare `date` object (only full `datetime`).



\*\*Fix applied and verified (all 22 tests pass):\*\*



Replace the final line of `save\_patent()`:



&#x20;   if ping\_mongo(): get\_mongo\_db()\["patents\_raw"].replace\_one({"external\_id":ext},{"external\_id":ext,"source":data.get("source"),"data":data.get("raw",data)},upsert=True)



With:



&#x20;   if ping\_mongo():

&#x20;       mongo\_data = {k: (v.isoformat() if isinstance(v, date) else v) for k, v in data.get("raw", data).items()}

&#x20;       get\_mongo\_db()\["patents\_raw"].replace\_one({"external\_id":ext},{"external\_id":ext,"source":data.get("source"),"data":mongo\_data},upsert=True)



Converts any `date`/`datetime` fields to ISO strings specifically for the Mongo write, without changing what's saved to Postgres.



\## 2. Backend architecture divergence across branches



Multiple members (kanishka, Anuhya-Kurakula, mayank) have independently restructured the backend differently — see team discussion on 2026-08-20. Team is reviewing each member's completed work before deciding on a shared structure. Currently proceeding with Anuhya's structure as the working base for integration testing.


## 3. backend/main.py (Milestone 3 app) fails to start — Anuhya-Kurakula branch, commit 83ab242

**Context:** Anuhya's branch has two coexisting FastAPI apps: `app/main.py` (old, Milestone 2 only) and `backend/main.py` (flat structure, wired up with the new Milestone 3 routers). `backend/main.py` is the one that should be canonical for Milestone 3, but it currently cannot start.

**Issue 1 — Missing model:**
`app/models/__init__.py` and `backend/models.py` both import `TechnologyDomain` from `app/models/research_assets.py`, but that class is not defined there (only `Publication` and `Patent` exist). Confirmed via `findstr` that `TechnologyDomain` is not referenced anywhere else in the codebase — likely a leftover/premature import.

**Issue 2 — Missing router files (blocking):**
`backend/main.py` imports `auth_routes`, `profile_routes`, `admin_routes`, `grant_matching_routes`, and `technology_routes` from `routers/`, but `routers/` only contains: `commercialization_routes.py`, `dataset_routes.py`, `patent_landscape_routes.py`, `scoring_routes.py`. The 5 other files referenced don't exist in the repo.

**Result:** `backend/main.py` fails on import before reaching any endpoint — confirmed by running `python -m uvicorn backend.main:app --reload --app-dir ..` from the scratch clone, which throws `ImportError: cannot import name 'TechnologyDomain'`.

**Status:** Flagged to Anuhya directly (2026-09-01). Not fixed locally — missing router files require knowing intended behavior, not something to guess/fabricate. Integration testing against `backend/main.py` is blocked until resolved.

