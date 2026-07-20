from functools import lru_cache
from typing import TYPE_CHECKING

import numpy as np

if TYPE_CHECKING:
    from sentence_transformers import SentenceTransformer

DEFAULT_MODEL = "all-MiniLM-L6-v2"


@lru_cache(maxsize=1)
def get_model(model_name: str = DEFAULT_MODEL) -> "SentenceTransformer":
    # Deliberately imported here, not at module top level: src/ranking.py
    # (via src/pipeline.py) now imports this module at FastAPI startup,
    # so a top-level `from sentence_transformers import SentenceTransformer`
    # would make every API test pay the ~15s import cost just from
    # importing app.backend.main, even tests that never call /rank.
    # Only an actual call to get_model()/encode() should pay it.
    from sentence_transformers import SentenceTransformer

    return SentenceTransformer(model_name)


def encode(text: str, model_name: str = DEFAULT_MODEL) -> np.ndarray:
    """
    Encode a single string into a dense embedding vector.

    Domain-agnostic by design: knows nothing about resumes, job
    descriptions, or any other document type — callers are
    responsible for deciding what text to pass in (see
    src/pipeline.py's prepare_resume_embedding_text() for the
    resume-specific case). Vector dimensionality is whatever
    model_name produces; never hardcode it elsewhere.

    Only single-string encoding is exercised today. The underlying
    SentenceTransformer.encode() call already accepts list[str] and
    returns a 2D array for batch input, so adding batch support later
    (e.g. for /rank scoring many candidates against one job) will not
    require a breaking change to this function's contract.

    Timing (measured, not assumed — see PROJECT_BIBLE.md Section 19):
    the first call in a fresh process pays for importing
    sentence_transformers/torch (~15s) plus loading model weights
    into memory (~6s if already downloaded, ~30s+ on a true first-ever
    download). Every call after that in the same process is fast
    (~20ms) since get_model() caches the loaded model. This makes
    embedding cheap in a long-lived server process but expensive to
    exercise naively in a test suite — see the `slow` pytest marker.
    """

    return get_model(model_name).encode(text)
