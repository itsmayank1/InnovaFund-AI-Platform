import re
from pathlib import Path
from datetime import datetime
import pandas as pd
from database import SessionLocal
from models import FundingOpportunity

DATA_DIR = Path(__file__).resolve().parent / "data"

def strip_html(text: str) -> str:
    return re.sub(r"<[^<]+?>", " ", str(text))

def extract_keywords(summary: str, n_words: int = 25) -> str:
    plain = strip_html(summary)
    words = re.findall(r"[A-Za-z]{4,}", plain)
    return " ".join(words[:n_words])

def load_from_csv(path: str = None):
    path = path or DATA_DIR / "funding_dataset.csv"
    df = pd.read_csv(path)

    df = df[df["opportunity_status"] == "posted"].copy()
    df = df.dropna(subset=["close_date"])

    db = SessionLocal()
    count = 0
    for _, row in df.iterrows():
        amount = row["award_ceiling"]
        if pd.isna(amount) or amount == 0:
            amount = row["estimated_total_program_funding"]
        amount = 0.0 if pd.isna(amount) else float(amount)

        domains = str(row["funding_categories"]).replace(";", ",") if pd.notna(row["funding_categories"]) else ""
        keywords = extract_keywords(row["summary_description"]) if pd.notna(row["summary_description"]) else domains

        opp = FundingOpportunity(
            title=row["opportunity_title"],
            agency=row["agency_name"] if pd.notna(row["agency_name"]) else "",
            domains=domains,
            research_domain=domains,
            keywords=keywords,
            amount=amount,
            deadline=datetime.strptime(row["close_date"], "%Y-%m-%d"),
            past_success_rate=0.2,
            url=row["url"] if pd.notna(row["url"]) else "",
        )
        db.add(opp)
        count += 1

    db.commit()
    db.close()
    print(f"Loaded {count} real funding opportunities (status=posted)")

if __name__ == "__main__":
    load_from_csv()