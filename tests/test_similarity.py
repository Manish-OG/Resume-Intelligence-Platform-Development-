import numpy as np

from src.similarity.compute import cosine_similarity


def test_cosine_similarity_identical_vectors():
    a = np.array([1.0, 2.0, 3.0])

    assert cosine_similarity(a, a) == 1.0


def test_cosine_similarity_orthogonal_vectors():
    a = np.array([1.0, 0.0])
    b = np.array([0.0, 1.0])

    assert cosine_similarity(a, b) == 0.0


def test_cosine_similarity_opposite_vectors():
    a = np.array([1.0, 0.0])
    b = np.array([-1.0, 0.0])

    assert cosine_similarity(a, b) == -1.0


def test_cosine_similarity_zero_vector_returns_zero():
    a = np.array([0.0, 0.0, 0.0])
    b = np.array([1.0, 2.0, 3.0])

    assert cosine_similarity(a, b) == 0.0


def test_cosine_similarity_scale_invariant():
    a = np.array([1.0, 2.0, 3.0])
    b = np.array([2.0, 4.0, 6.0])

    assert cosine_similarity(a, b) == 1.0
