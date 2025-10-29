import re
from typing import Iterable, List

_WHITESPACE_RE = re.compile(r"\s+")


def normalize_text(value: str) -> str:
    if value is None:
        return ""
    text = value.strip()
    text = _WHITESPACE_RE.sub(" ", text)
    return text


def take_last(items: Iterable[str], n: int) -> List[str]:
    arr = list(items)
    if n <= 0:
        return []
    return arr[-n:]

