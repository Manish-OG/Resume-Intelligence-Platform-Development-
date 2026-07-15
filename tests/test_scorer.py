from src.scorer.weighted_scorer import ScoreComponents, compute_score


def test_compute_score_default_weights():
    components = ScoreComponents(semantic=1.0, skills=1.0, experience=1.0, education=1.0)
    assert compute_score(components) == 1.0


def test_compute_score_zero():
    components = ScoreComponents(semantic=0.0, skills=0.0, experience=0.0, education=0.0)
    assert compute_score(components) == 0.0
