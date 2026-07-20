import numpy as np
import pytest

from src.similarity.compute import cosine_similarity

pytestmark = pytest.mark.slow

# `encode` is imported inside each test, not at module level: pytest
# imports this module during collection even when its tests are
# deselected (the default, via pytest.ini's `-m "not slow"`), and a
# module-level `from src.embeddings.encoder import encode` would pay
# the ~15s sentence_transformers/torch import cost on every default
# test run regardless of whether these tests actually execute. This
# was caught by measuring, not assumed — see PROJECT_BIBLE.md Section 11.


def test_encode_returns_nonempty_float_vector():
    from src.embeddings.encoder import encode

    vector = encode("Senior backend engineer with Python experience")

    assert isinstance(vector, np.ndarray)
    assert vector.ndim == 1
    assert vector.shape[0] > 0  # dimensionality intentionally not hardcoded
    assert np.issubdtype(vector.dtype, np.floating)


def test_similar_sentences_score_higher_than_unrelated_ones():
    from src.embeddings.encoder import encode

    query = encode("Looking for a backend engineer skilled in Python and APIs")
    similar = encode("Backend developer with 5 years of Python and REST API experience")
    unrelated = encode("Recipe for chocolate chip cookies with butter and sugar")

    similar_score = cosine_similarity(query, similar)
    unrelated_score = cosine_similarity(query, unrelated)

    assert similar_score > unrelated_score


def test_identical_text_scores_near_one():
    from src.embeddings.encoder import encode

    text = "Full-stack engineer with React and Node.js experience"

    a = encode(text)
    b = encode(text)

    assert cosine_similarity(a, b) == pytest.approx(1.0, abs=1e-5)


def test_get_model_returns_cached_instance_across_calls():
    from src.embeddings.encoder import DEFAULT_MODEL, get_model

    first = get_model(DEFAULT_MODEL)
    second = get_model(DEFAULT_MODEL)

    assert first is second
