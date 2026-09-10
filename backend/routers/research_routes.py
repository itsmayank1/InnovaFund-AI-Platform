import os
import requests
from fastapi import APIRouter, HTTPException

router = APIRouter(tags=["Research & Patents"])

@router.get("/publications/search")
def search_publications(query: str, limit: int = 10):
    url = "https://api.openalex.org/works"
    params = {"search": query, "per-page": limit}
    try:
        response = requests.get(url, params=params, timeout=10)
    except requests.RequestException:
        raise HTTPException(status_code=502, detail="Failed to connect to OpenAlex")
    if response.status_code != 200:
        raise HTTPException(status_code=502, detail="Failed to fetch data from OpenAlex")
    data = response.json()
    results = []
    for work in data.get("results", []):
        results.append({
            "title": work.get("title"),
            "publication_year": work.get("publication_year"),
            "doi": work.get("doi"),
            "cited_by_count": work.get("cited_by_count"),
            "authors": [a["author"]["display_name"] for a in work.get("authorships", []) if "author" in a],
        })
    return {"query": query, "count": len(results), "results": results}

PATENTSVIEW_API_KEY = os.getenv("PATENTSVIEW_API_KEY")

@router.get("/patents/search")
def search_patents(query: str, limit: int = 10):
    if not PATENTSVIEW_API_KEY:
        raise HTTPException(
            status_code=503,
            detail="Patent search not yet configured. Add PATENTSVIEW_API_KEY to .env once you receive it.",
        )
    url = "https://search.patentsview.org/api/v1/patent/"
    headers = {"X-Api-Key": PATENTSVIEW_API_KEY}
    params = {
        "q": f'{{"_text_any":{{"patent_title":"{query}"}}}}',
        "f": '["patent_id","patent_title","patent_date"]',
        "o": f'{{"size":{limit}}}',
    }
    try:
        response = requests.get(url, headers=headers, params=params, timeout=10)
    except requests.RequestException:
        raise HTTPException(status_code=502, detail="Failed to connect to PatentsView")
    if response.status_code != 200:
        raise HTTPException(status_code=502, detail=f"Failed to fetch patent data: {response.text}")
    return response.json()
