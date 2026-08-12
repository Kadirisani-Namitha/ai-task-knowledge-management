import logging
from functools import lru_cache

import numpy as np
from sentence_transformers import SentenceTransformer

logger = logging.getLogger(__name__)

MODEL_NAME = "all-MiniLM-L6-v2"


@lru_cache(maxsize=1)
def _load_model() -> SentenceTransformer:
    logger.info("Loading embedding model: %s", MODEL_NAME)
    model = SentenceTransformer(MODEL_NAME)
    logger.info("Embedding model loaded (dimension=%d)", model.get_sentence_embedding_dimension())
    return model


def get_embedding_dimension() -> int:
    return _load_model().get_sentence_embedding_dimension()


def embed_texts(texts: list[str]) -> np.ndarray:
    """Encode a batch of texts into normalized float32 vectors."""
    model = _load_model()
    vectors = model.encode(texts, convert_to_numpy=True, normalize_embeddings=True)
    return vectors.astype(np.float32)


def embed_query(query: str) -> np.ndarray:
    """Encode a single query string."""
    return embed_texts([query])[0]
