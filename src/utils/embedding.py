from typing import List
import numpy as np
from openai import OpenAI
from ..config import settings

_client = None


def _client_instance() -> OpenAI:
    global _client
    if _client is None:
        _client = OpenAI(api_key=settings.openai.api_key)
    return _client


def embed_texts(texts: List[str]) -> List[List[float]]:
    client = _client_instance()
    resp = client.embeddings.create(model=settings.openai.embedding_model, input=texts)
    return [d.embedding for d in resp.data]


def cosine_similarity(vec_a: List[float], vec_b: List[float]) -> float:
    a = np.array(vec_a)
    b = np.array(vec_b)
    denom = (np.linalg.norm(a) * np.linalg.norm(b))
    if denom == 0:
        return 0.0
    return float(np.dot(a, b) / denom)









