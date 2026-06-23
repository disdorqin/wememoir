"""JSONL importer: one JSON message per line."""

from __future__ import annotations

import uuid
from datetime import datetime
from pathlib import Path

from ..models import Conversation, Message, SENDER_UNKNOWN, MSG_UNKNOWN


def import_jsonl(path: str) -> Conversation:
    p = Path(path)
    msgs: list[Message] = []
    for i, line in enumerate(p.read_text(encoding="utf-8").splitlines()):
        line = line.strip()
        if not line:
            continue
        import json
        data = json.loads(line)
        ts = data.get("timestamp")
        if isinstance(ts, str):
            try:
                ts = datetime.fromisoformat(ts)
            except ValueError:
                ts = datetime.utcnow()
        elif not isinstance(ts, datetime):
            ts = datetime.utcnow()
        msgs.append(
            Message(
                id=str(data.get("id", f"jsonl_{i}_{uuid.uuid4().hex[:6]}")),
                timestamp=ts,
                sender=str(data.get("sender", "")),
                sender_type=str(data.get("sender_type", SENDER_UNKNOWN)),
                message_type=str(data.get("message_type", MSG_UNKNOWN)),
                content=str(data.get("content", "")),
                raw_content=str(data.get("raw_content", data.get("content", ""))),
                source=str(data.get("source", "jsonl")),
                conversation_name=str(data.get("conversation_name", "")),
            )
        )
    msgs.sort(key=lambda m: m.timestamp)
    return Conversation(
        id=str(uuid.uuid4()),
        name=p.stem,
        type="private",
        participants=sorted({m.sender for m in msgs if m.sender}),
        messages=msgs,
        source="jsonl",
    )
