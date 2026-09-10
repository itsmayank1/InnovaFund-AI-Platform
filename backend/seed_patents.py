"""
seed_patents.py
----------------
One-time / re-runnable script to load lens-export.csv into the local
patent_records table (PatentRecord model) for Milestone 3 testing.

- Safe to run multiple times: clears patent_records before each reseed,
  so it never creates duplicates.
- Maps Lens.org CSV columns -> PatentRecord fields.
- Handles missing Applicants/Owners, missing/invalid dates, and
  missing/invalid citation counts without crashing.
- technology_domain is DERIVED from the first CPC classification code
  (approximate, not authoritative -- documented for the team).
- This writes to whatever database your app is currently connected to
  (local SQLite fallback right now). It does NOT touch any shared
  team database or Member 8's schema.
"""

import sys
import pandas as pd
from sqlalchemy import text
from sqlalchemy.orm import Session
from database import engine
from models import PatentRecord

CSV_PATH = "lens-export.csv"

# CPC section letter -> rough technology domain (approximation only)
CPC_DOMAIN_MAP = {
    "A": "Human Necessities",
    "B": "Operations & Transport",
    "C": "Chemistry & Metallurgy",
    "D": "Textiles",
    "E": "Fixed Constructions",
    "F": "Mechanical Engineering",
    "G": "Physics & Computing",
    "H": "Electricity",
    "Y": "Emerging/Cross-Sector Tech",
}

REQUIRED_COLUMNS = [
    "Title", "Applicants", "Owners", "Application Date",
    "Publication Date", "CPC Classifications", "Cited by Patent Count", "Abstract"
]


def derive_domain(cpc_value):
    if pd.isna(cpc_value) or not str(cpc_value).strip():
        return "Unclassified"
    first_code = str(cpc_value).split(";")[0].strip()
    section = first_code[0] if first_code else ""
    return CPC_DOMAIN_MAP.get(section, "Unclassified")


def main():
    print(f"Loading {CSV_PATH} ...")
    try:
        df = pd.read_csv(CSV_PATH)
    except FileNotFoundError:
        print(f"ERROR: {CSV_PATH} not found. Make sure it's in the backend/ folder.")
        sys.exit(1)

    print(f"Loaded {len(df)} rows, {len(df.columns)} columns.")

    # Check every column we need actually exists before mapping anything
    missing = [c for c in REQUIRED_COLUMNS if c not in df.columns]
    if missing:
        print("ERROR: These expected columns are missing from your CSV:")
        for m in missing:
            print(f"  - {m}")
        print("\nActual columns in your file:")
        print(list(df.columns))
        print("\nFix: compare the two lists above and tell me the mismatches.")
        sys.exit(1)

    mapped = pd.DataFrame()
    mapped["title"] = df["Title"]
    mapped["assignee"] = df["Applicants"].fillna(df["Owners"]).fillna("Unknown")
    mapped["filing_date"] = pd.to_datetime(
        df["Application Date"].fillna(df["Publication Date"]), errors="coerce"
    )
    mapped["classification"] = df["CPC Classifications"].apply(
        lambda x: str(x).split(";")[0].strip() if pd.notna(x) else None
    )
    mapped["technology_domain"] = df["CPC Classifications"].apply(derive_domain)
    mapped["citation_count"] = pd.to_numeric(
        df["Cited by Patent Count"], errors="coerce"
    ).fillna(0).astype(int)
    mapped["abstract"] = df["Abstract"]

    before = len(mapped)
    mapped = mapped.dropna(subset=["title"])
    dropped = before - len(mapped)
    print(f"Dropped {dropped} rows with no title.")

    
    # Clear existing local patent records and insert cleaned CSV data
    # using SQLAlchemy ORM instead of pandas.to_sql().
    with Session(engine) as db:
        db.query(PatentRecord).delete(synchronize_session=False)

        records = []

        for _, row in mapped.iterrows():
            record = PatentRecord(
                title=str(row["title"]),
                assignee=row["assignee"],
                filing_date=row["filing_date"].date()
                    if pd.notna(row["filing_date"])
                    else None,
                classification=row["classification"],
                technology_domain=row["technology_domain"],
                citation_count=int(row["citation_count"]),
                abstract=row["abstract"]
            )
            records.append(record)

        db.bulk_save_objects(records)
        db.commit()

    print(
        f"Cleared existing rows and inserted "
        f"{len(records)} rows into patent_records."
    )


if __name__ == "__main__":
    main()