from functools import lru_cache

from sentence_transformers import SentenceTransformer

DEFAULT_MODEL = "all-MiniLM-L6-v2"


@lru_cache(maxsize=1)
def get_model(model_name: str = DEFAULT_MODEL) -> SentenceTransformer:
    return SentenceTransformer(model_name)


def encode(text: str, model_name: str = DEFAULT_MODEL):
    return get_model(model_name).encode(text)
