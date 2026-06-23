from __future__ import annotations

from ..models import Message


def deduplicate(messages: list[Message]) -> list[Message]:
    """移除相邻的完全重复消息（同一发送者、同内容、同类型）。"""
    result: list[Message] = []
    for m in messages:
        if (
            result
            and result[-1].sender == m.sender
            and result[-1].content == m.content
            and result[-1].message_type == m.message_type
        ):
            continue
        result.append(m)
    return result
