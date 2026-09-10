# Antigravity IDE Workspace Rules: InnovaFund-AI

## Project Architecture
- **Backend**: FastAPI (Python 3.11/3.14), SQLAlchemy ORM, PyTest.
- **Frontend**: React 18 + Vite + Tailwind CSS (`frontend/src/`).
- **Database**: PostgreSQL 16 (fallback to local `funding_innovation_platform.db` SQLite) + MongoDB 7.

## Key Member Roles
- **Member 2 Scope**: Grant Matching Workflows (`/api/grants/*`) & Technology Intelligence Engine (`/api/technology/*`).

## Verification & Testing Standards
- Test suite command: `python -m pytest backend/tests/test_grant_matching.py backend/tests/test_technology_intelligence.py`
- Frontend build command: `npm run build` inside `frontend/`
- Git branch: `mayank` on remote `official` (`https://github.com/springboardmentor825/Research-Funding-Innovation-Team-3.git`)
