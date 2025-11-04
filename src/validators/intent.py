from dataclasses import dataclass
from typing import Tuple
from openai import OpenAI
from ..config import settings

_client = None


def _client_instance() -> OpenAI:
    global _client
    if _client is None:
        _client = OpenAI(
            api_key=settings.openai.api_key,
            base_url=settings.openai.base_url
        )
    return _client


@dataclass
class IntentResult:
    decision: bool
    confidence: float
    raw: str


_SYSTEM_PROMPT = (
    "You are a strict evaluator. Answer strictly in JSON with keys: decision (yes/no), confidence (0..1)."
)


def check_intent(answer_text: str, intent_description: str) -> IntentResult:
    client = _client_instance()
    user_prompt = (
        f"Answer: {answer_text}\n\n"
        f"Question: Does the answer express the intent: '{intent_description}'?"
    )
    resp = client.chat.completions.create(
        model=settings.openai.chat_model,
        messages=[
            {"role": "system", "content": _SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0.0,
    )
    content = resp.choices[0].message.content or ""
    try:
        import json

        data = json.loads(content)
        decision_raw = str(data.get("decision", "no")).strip().lower()
        decision = decision_raw.startswith("y")
        confidence = float(data.get("confidence", 0))
    except Exception:
        decision = False
        confidence = 0.0
    return IntentResult(decision=decision, confidence=confidence, raw=content)


def validate_intent(answer_text: str, intent_description: str, min_confidence: float | None = None) -> Tuple[bool, IntentResult]:
    thr = min_confidence if min_confidence is not None else settings.thresholds.intent_confidence_min
    result = check_intent(answer_text, intent_description)
    return (result.decision and result.confidence >= thr, result)
