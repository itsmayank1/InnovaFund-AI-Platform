from datetime import datetime, timedelta
from recommendation_engine import domain_fit_score, deadline_score, amount_score, compute_score

class FakeOpportunity:
    def __init__(self, domains, keywords, amount, deadline_days, success_rate):
        self.domains = domains
        self.keywords = keywords
        self.amount = amount
        self.deadline = datetime.utcnow() + timedelta(days=deadline_days)
        self.past_success_rate = success_rate

def test_domain_fit_high_overlap():
    score = domain_fit_score("Artificial Intelligence Machine Learning",
                              "Artificial Intelligence Neural Networks")
    assert score > 0.1

def test_domain_fit_no_overlap():
    score = domain_fit_score("Marine Biology", "Quantum Computing")
    assert score == 0.0 or score < 0.05

def test_deadline_too_soon_scores_low():
    assert deadline_score(datetime.utcnow() + timedelta(days=2)) == 0.1

def test_deadline_sweet_spot_scores_high():
    assert deadline_score(datetime.utcnow() + timedelta(days=30)) == 1.0

def test_deadline_expired_scores_zero():
    assert deadline_score(datetime.utcnow() - timedelta(days=1)) == 0.0

def test_amount_score_normalizes():
    score = amount_score(150000, 100000, 200000)
    assert 0.0 < score < 1.0

def test_compute_score_ranks_better_fit_higher():
    good_fit = FakeOpportunity("Artificial Intelligence", "machine learning neural networks",
                                150000, 30, 0.2)
    bad_fit = FakeOpportunity("Marine Biology", "ocean conservation coral reefs",
                                150000, 30, 0.2)
    profile_text = "Artificial Intelligence machine learning deep learning"

    good_result = compute_score(profile_text, good_fit, 100000, 200000)
    bad_result = compute_score(profile_text, bad_fit, 100000, 200000)

    assert good_result["score"] > bad_result["score"]