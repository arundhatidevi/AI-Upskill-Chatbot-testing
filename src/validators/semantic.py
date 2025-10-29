from dataclasses import dataclass
from ..config import settings
from ..utils.embedding import embed_texts, cosine_similarity


@dataclass
class SemanticResult:
    similarity: float
    passed: bool


def validate_semantic_similarity(expected: str, actual: str, threshold: float | None = None) -> SemanticResult:
    thr = threshold if threshold is not None else settings.thresholds.semantic_similarity_min
    expected_emb, actual_emb = embed_texts([expected, actual])
    sim = cosine_similarity(expected_emb, actual_emb)
    return SemanticResult(similarity=sim, passed=sim >= thr)


