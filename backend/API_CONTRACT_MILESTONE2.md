\# Milestone 2 API Contract — Funding Discovery \& Research Trends



Documents the working endpoints for the Funding Discovery and Research Trend Intelligence modules, as implemented on the Anuhya-Kurakula branch (current working base while the team finalizes a shared backend structure — see QA\_FINDINGS.md). Frontend and QA should build against this.



\---



\## Funding Discovery



\### GET /api/v1/funding/opportunities



Lists funding opportunities, optionally filtered.



\*\*Auth:\*\* not required



| Query param | Type | Required | Notes |

|---|---|---|---|

| `q` | string | no | Free-text search against opportunity title/description |

| `source\_type` | string | no | One of: Government Grants, Research Councils, Innovation Funds, Startup Accelerators, Venture Programs, International Funding Agencies |



\*\*Response — 200 OK:\*\* list of funding opportunity objects.



\---



\### GET /api/v1/funding/recommendations



Returns personalized funding matches for the logged-in user, based on their research profile.



\*\*Auth:\*\* required (Bearer token)



\*\*Response — 200 OK:\*\* list of recommendation objects, each including `match\_score`.



\---



\### GET /api/v1/funding/alerts



Returns a short list (up to 5) of high-priority funding alerts for the logged-in user.



\*\*Auth:\*\* required (Bearer token)



\*\*Response — 200 OK:\*\* list of recommendation objects, same shape as `/funding/recommendations`.



\---



\### POST /api/v1/funding/opportunities



Creates a new funding opportunity. Admin only.



\*\*Auth:\*\* required, ADMINISTRATOR role only — returns 403 for other roles.



\*\*Response — 201 Created:\*\* the created funding opportunity object.



\---



\### POST /api/v1/profile/funding/{opportunity\_id}



Bookmarks a funding opportunity to the logged-in user's profile.



\*\*Auth:\*\* required (Bearer token)



\*\*Path param:\*\* `opportunity\_id` (int)



\*\*Response — 201 Created:\*\* the bookmarked funding opportunity object.



\---



\### GET /api/v1/profile/funding



Lists the logged-in user's bookmarked funding opportunities.



\*\*Auth:\*\* required (Bearer token)



\*\*Response — 200 OK:\*\* list of funding opportunity objects.



\---



\## Research Trend Intelligence



\### GET /api/v1/trends/topics



Returns trending research topics.



\*\*Auth:\*\* not required



\*\*Response — 200 OK:\*\*

```json

{ "topics": \[ ... ] }

```



\---



\### GET /api/v1/trends/hotspots



Returns research hotspots and associated domains.



\*\*Auth:\*\* not required



\*\*Response — 200 OK:\*\*

```json

{ "hotspots": \[ ... ], "domains": \[ ... ] }

```



\---



\### GET /api/v1/trends/citations



Returns citation analytics across analyzed publications.



\*\*Auth:\*\* not required



\*\*Response — 200 OK:\*\*

```json

{

&#x20; "total\_publications\_analyzed": 0,

&#x20; "total\_citations": 0,

&#x20; "average\_citations\_per\_paper": 0,

&#x20; "top\_cited\_publications": \[ ... ]

}

```



\---



\## Notes for Member 8 (QA) / self



\- Full cross-module flow (profile → publications/patents → funding recommendations → trends) covered in `backend/test\_integration\_workflow.py`.

\- Known bug found and fixed: patent-save endpoint previously crashed on BSON date encoding — see `QA\_FINDINGS.md`.

\- Response shapes above are taken directly from `app/api/funding.py` and `app/api/trends.py` on the Anuhya-Kurakula branch as of 2026-08-20. Will need revision once the team finalizes a shared backend structure.



