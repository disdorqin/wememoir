from __future__ import annotations

from datetime import datetime

from wememoir.memoir import MemoirWriter
from wememoir.models import Conversation, Message


def _conv(messages_data):
    messages = [
        Message(
            id=f"m{i}",
            timestamp=datetime.fromisoformat(ts),
            sender=sender,
            content=content,
            raw_content=content,
        )
        for i, (ts, sender, content) in enumerate(messages_data)
    ]
    return Conversation(
        id="c1",
        name="Alice",
        type="private",
        participants=["Me", "Alice"],
        messages=messages,
    )


def test_memoir_structure(tmp_path):
    conv = _conv(
        [
            ("2023-01-01T10:00:00", "Alice", "你好"),
            ("2023-01-01T10:01:00", "Me", "你好呀"),
            ("2023-02-15T22:00:00", "Alice", "明天见"),
            ("2023-02-15T22:05:00", "Me", "好的，晚安"),
        ]
    )
    out = tmp_path / "memoir.md"
    writer = MemoirWriter(conv)
    text = writer.write(str(out))
    assert out.exists()
    assert "聊天回忆录" in text
    assert "## 初识期" in text
    assert "## " in text
