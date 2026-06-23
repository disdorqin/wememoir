"""Extract mom's real high-frequency phrases and representative quotes."""

from __future__ import annotations

from collections import Counter
from typing import Dict, List

from ..models import Message


def _normalise(text: str) -> str:
    return (text or "").strip()


def extract_phrases(messages: List[Message], mom_name: str) -> Dict[str, object]:
    mom_msgs = [m for m in messages if m.sender == mom_name or m.sender_type == "mom"]
    counter: Counter = Counter()
    first_seen: Dict[str, str] = {}
    last_seen: Dict[str, str] = {}
    context: Dict[str, List[str]] = {}

    for m in mom_msgs:
        text = _normalise(m.content)
        if not text:
            continue
        counter[text] += 1
        ts = m.timestamp.isoformat() if hasattr(m.timestamp, "isoformat") else str(m.timestamp)
        if text not in first_seen:
            first_seen[text] = ts
        last_seen[text] = ts
        context.setdefault(text, []).append(text)

    phrases = []
    for text, count in counter.most_common(200):
        phrases.append(
            {
                "phrase": text,
                "count": count,
                "first_seen": first_seen.get(text, ""),
                "last_seen": last_seen.get(text, ""),
                "context_examples": context.get(text, [])[:3],
            }
        )
    return {"mom_name": mom_name, "total_unique": len(phrases), "phrases": phrases}
