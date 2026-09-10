from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from datetime import datetime
import math

WEIGHTS = {
    "domain_fit": 0.60,
    "deadline": 0.10,
    "amount": 0.10,
    "success_rate": 0.20,
}

def domain_fit_score(profile_text: str, opportunity_text: str) -> float:
    if not profile_text.strip() or not opportunity_text.strip():
        return 0.0
    vectorizer = TfidfVectorizer()
    try:
        tfidf = vectorizer.fit_transform([profile_text, opportunity_text])
        sim = cosine_similarity(tfidf[0:1], tfidf[1:2])[0][0]
        return round(float(sim), 4)
    except ValueError:
        return 0.0

def deadline_score(deadline, now=None) -> float:
    from datetime import datetime, date
    now_date = now.date() if isinstance(now, datetime) else (now or datetime.utcnow().date())
    deadline_date = deadline.date() if isinstance(deadline, datetime) else deadline
    days_left = (deadline_date - now_date).days
    if days_left < 0:
        return 0.0
    if days_left < 7:
        return 0.1
    if 7 <= days_left <= 90:
        return 1.0
    if 90 < days_left <= 180:
        return 0.7
    return 0.4

def amount_score(amount, min_amount: float, max_amount: float) -> float:
    amount = amount or 0.0  # handles None safely
    if max_amount == min_amount:
        return 0.5

    log_amount = math.log(amount + 1)
    log_min = math.log(min_amount + 1)
    log_max = math.log(max_amount + 1)

    if log_max == log_min:
        return 0.5

    score = (log_amount - log_min) / (log_max - log_min)
    return round(max(0.0, min(1.0, score)), 4)

def build_reasoning(d_score, dl_score, amt_score, sr_score) -> str:
    parts = []
    parts.append("Strong domain fit" if d_score > 0.4 else "Weak domain fit" if d_score < 0.15 else "Moderate domain fit")
    parts.append("deadline gives enough prep time" if dl_score >= 0.7 else "deadline is tight or far off")
    parts.append("competitive funding amount" if amt_score > 0.6 else "modest funding amount")
    parts.append("historically good odds" if sr_score > 0.2 else "historically competitive odds")
    return ", ".join(parts).capitalize() + "."

def build_opportunity_text(opportunity) -> str:
    """
    Combine every text field that might describe this opportunity's topic.
    Falls back to the teammate's original fields (research_domain, description)
    if this engine's own fields (domains, keywords) are empty.
    """
    parts = []
    if getattr(opportunity, "domains", None):
        parts.append(opportunity.domains)
    if getattr(opportunity, "keywords", None):
        parts.append(opportunity.keywords)
    if getattr(opportunity, "research_domain", None):
        parts.append(opportunity.research_domain)
    if getattr(opportunity, "description", None):
        parts.append(opportunity.description)
    return " ".join(parts)

def get_opportunity_amount(opportunity):
    """Prefer this engine's `amount` field; fall back to the teammate's `grant_amount`."""
    if getattr(opportunity, "amount", None):
        return opportunity.amount
    return getattr(opportunity, "grant_amount", None)

def compute_score(profile_text: str, opportunity, min_amount: float, max_amount: float) -> dict:
    opportunity_text = build_opportunity_text(opportunity)
    opportunity_amount = get_opportunity_amount(opportunity)

    d_score = domain_fit_score(profile_text, opportunity_text)
    dl_score = deadline_score(opportunity.deadline)
    amt_score = amount_score(opportunity_amount, min_amount, max_amount)
    sr_score = round(opportunity.past_success_rate or 0.0, 4)

    final = (
        d_score * WEIGHTS["domain_fit"]
        + dl_score * WEIGHTS["deadline"]
        + amt_score * WEIGHTS["amount"]
        + sr_score * WEIGHTS["success_rate"]
    ) * 100

    return {
        "domain_fit_score": d_score,
        "deadline_score": dl_score,
        "amount_score": amt_score,
        "success_rate_score": sr_score,
        "score": round(final, 2),
        "reasoning": build_reasoning(d_score, dl_score, amt_score, sr_score),
    }

def build_profile_text(profile) -> str:
    parts = []
    if profile.interests:
        parts.append(" ".join(i.domain_name for i in profile.interests if i.domain_name))
    if profile.keywords:
        parts.append(" ".join(k.keyword_name for k in profile.keywords if k.keyword_name))
    if profile.technology_areas:
        parts.append(profile.technology_areas)
    return " ".join(parts)