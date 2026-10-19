from functools import lru_cache


EMBEDDING_MODEL_NAME = "BAAI/bge-small-zh-v1.5"


@lru_cache(maxsize=1)
def _get_embedding_model():
    """Load the embedding model lazily."""
    try:
        from sentence_transformers import SentenceTransformer

        return SentenceTransformer(EMBEDDING_MODEL_NAME)
    except Exception:
        return None


def embed_text(text: str) -> list[float]:
    """Return embedding vectors or an empty list if model loading fails."""
    model = _get_embedding_model()
    if model is None:
        return []

    try:
        vector = model.encode(text)
        return vector.tolist()
    except Exception:
        return []
