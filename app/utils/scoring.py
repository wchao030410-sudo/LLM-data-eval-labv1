import math
import re
from collections import Counter
from typing import Dict, Iterable, List


def normalize_text(text: str) -> List[str]:
    normalized = (text or "").lower()
    tokens: List[str] = []
    for chunk in re.findall(r"[\u4e00-\u9fff]+|[a-z0-9]+", normalized):
        if re.fullmatch(r"[\u4e00-\u9fff]+", chunk):
            tokens.extend(list(chunk))
        else:
            tokens.append(chunk)
    return tokens


def token_overlap_ratio(left: str, right: str) -> float:
    left_tokens = Counter(normalize_text(left))
    right_tokens = Counter(normalize_text(right))
    if not right_tokens:
        return 0.0
    overlap = sum((left_tokens & right_tokens).values())
    total = sum(right_tokens.values())
    return min(1.0, overlap / max(total, 1))


def groundedness_ratio(answer: str, context: str) -> float:
    answer_tokens = set(normalize_text(answer))
    context_tokens = set(normalize_text(context))
    if not answer_tokens:
        return 0.0
    covered = len(answer_tokens & context_tokens) / max(len(answer_tokens), 1)
    novelty_penalty = math.exp(-max(len(answer_tokens - context_tokens), 0) / 10.0)
    return min(1.0, covered * 0.8 + novelty_penalty * 0.2)


def format_compliance_score(answer: str) -> float:
    answer = (answer or "").strip()
    if not answer:
        return 0.0
    if answer.startswith("{") and answer.endswith("}"):
        return 1.0
    if answer.startswith("- ") or answer.startswith("1. ") or answer.startswith("1、") or answer.startswith("•"):
        return 0.95
    if "\n" in answer and (":" in answer or "：" in answer):
        return 0.85
    compact_length = len(answer.replace(" ", ""))
    return 0.75 if compact_length >= 12 else 0.55


def average_metric(records: Iterable[Dict], key: str) -> float:
    values = [float(record.get(key, 0.0)) for record in records]
    if not values:
        return 0.0
    return round(sum(values) / len(values), 4)
