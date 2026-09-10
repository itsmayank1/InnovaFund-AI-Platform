# Recommendations API — Contract

This document describes the two endpoints built for the Funding Recommendation Engine (Milestone 2). Frontend and QA should build against this.

---

## POST /recommendations/generate

Scores every funding opportunity currently in the database against a researcher's profile, saves all results, and returns the top N matches.

**Requires:** the researcher must already have a research profile created via `POST /profile`.

### Request body

```json
{
  "researcher_id": 4,
  "top_n": 10
}
```

| Field | Type | Required | Notes |
|---|---|---|---|
| `researcher_id` | int | yes | Must correspond to an existing user with a research profile |
| `top_n` | int | no | Defaults to 10 if omitted |

### Response — 200 OK

Returns a list of recommendation objects (see shape below), sorted by score, highest first.

### Error responses

| Code | Meaning |
|---|---|
| 404 | No research profile found for this researcher_id — they need to create one first via POST /profile |
| 404 | No funding opportunities exist in the database at all |

---

## GET /recommendations/{researcher_id}

Reads back previously generated recommendations for a researcher. Does not recalculate anything — purely reads from the database.

### Path parameter

| Field | Type | Notes |
|---|---|---|
| `researcher_id` | int | The researcher whose saved recommendations to fetch |

### Response — 200 OK

Same recommendation object shape as above, sorted by score, highest first.

### Error responses

| Code | Meaning |
|---|---|
| 404 | No recommendations found for this researcher — call POST /recommendations/generate first |

---

## Recommendation object shape

Both endpoints return a list of objects in this exact shape:

```json
{
  "opportunity_id": 2,
  "title": "Mathematical Foundations of Artificial Intelligence",
  "agency": "U.S. National Science Foundation",
  "amount": 1500000,
  "deadline": "2026-10-09T00:00:00",
  "url": "https://simpler.grants.gov/opportunity/508e8ee7-6925-4593-a548-66578974572f",
  "score": 30.33,
  "domain_fit_score": 0.1843,
  "deadline_score": 1.0,
  "amount_score": 0.5267,
  "success_rate_score": 0.2,
  "eligible": true,
  "reasoning": "Moderate domain fit, deadline gives enough prep time, modest funding amount, historically competitive odds."
}
```

| Field | Type | Description |
|---|---|---|
| `opportunity_id` | int | ID of the matched funding opportunity |
| `title` | string | Grant title |
| `agency` | string or null | Funding agency name |
| `amount` | float or null | Funding amount in USD |
| `deadline` | datetime or null | Application deadline (ISO 8601) |
| `url` | string or null | Link to the opportunity |
| `score` | float | Final ranked score, 0–100. Higher = better match |
| `domain_fit_score` | float | 0–1, how well the research topic matches |
| `deadline_score` | float | 0–1, how favorable the deadline timing is |
| `amount_score` | float | 0–1, relative funding amount within this batch |
| `success_rate_score` | float | 0–1, historical success rate (currently mocked at 0.2 for all opportunities, pending real data from Member 3) |
| `eligible` | bool | **Placeholder — currently always `true`.** Will reflect Member 2's eligibility-matching logic once available |
| `reasoning` | string | Human-readable one-line explanation of the score, ready to display directly in UI |

---

## Notes for Member 7 (Frontend)

- Always check for a 404 on `GET /recommendations/{researcher_id}` — it means the researcher hasn't generated recommendations yet. Show a "Generate Recommendations" button in that case, which calls `POST /recommendations/generate`.
- `reasoning` is meant to be displayed as-is, no need to build your own explanation text.
- `score` is 0–100, useful directly for a progress bar or badge.

## Notes for Member 8 (QA)

- Unit tests for the scoring math itself already exist in `test_recommendation_engine.py` (7 tests, all passing) — focus your testing on the API layer and integration, not the scoring formulas.
- Known edge cases to verify: researcher with no profile, nonexistent researcher_id, empty funding_opportunities table, calling `/generate` twice in a row for the same researcher (should overwrite, not duplicate).