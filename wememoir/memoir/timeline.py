from __future__ import annotations

from ..models import Message


def build_timeline(messages: list[Message]) -> list[Message]:
    return sorted(messages, key=lambda m: m.timestamp)
