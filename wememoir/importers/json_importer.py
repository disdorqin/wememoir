from __future__ import annotations

import json
import uuid
from datetime import datetime
from pathlib import Path

from dateutil import parser as date_parser

from ..models import Conversation, Message


def _parse_timestamp(value) -> datetime:
    if isinstance(value, datetime):
        return value
    if not isinstance(value, str):
        return datetime.utcnow()
    try:
        return date_parser.parse(value, fuzzy=True)
    except Exception:
        return datetime.utcnow()


def _classify_message_type(content: str) -> str:
    text = content.strip()
    mapping = {
        "[图片]": "image",
        "[语音]": "audio",
        "[视频]": "video",
        "[红包]": "redpacket",
        "[转账]": "transfer",
    }
    return mapping.get(text, "text")


def _message_from_dict(m: dict) -> Message:
    content = m.get("content", m.get("text", m.get("message", "")))
    sender = m.get("sender", m.get("from", m.get("sender_name", "unknown")))
    msg_type = m.get("message_type", m.get("type", ""))
    if not msg_type:
        msg_type = _classify_message_type(content)
    return Message(
        id=str(uuid.uuid4()),
        timestamp=_parse_timestamp(m.get("timestamp", m.get("time", m.get("date", "")))),
        sender=sender,
        sender_type=m.get("sender_type", "other"),
        message_type=msg_type,
        content=content,
        raw_content=m.get("raw_content", content),
    )


def import_json(path: str) -> Conversation:
    p = Path(path)
    raw = json.loads(p.read_text(encoding="utf-8-sig"))

    if isinstance(raw, dict):
        if "messages" in raw:
            messages = [_message_from_dict(m) for m in raw.get("messages", [])]
            participants = list(raw.get("participants", []))
            if not participants:
                participants = sorted({m.sender for m in messages})
            return Conversation(
                id=raw.get("id", str(uuid.uuid4())),
                name=raw.get("name", p.stem),
                type=raw.get("type", "private"),
                participants=participants,
                messages=messages,
            )
        # Single message object
        raw = [raw]

    messages = [_message_from_dict(m) for m in raw]
    participants = sorted({m.sender for m in messages})
    return Conversation(
        id=str(uuid.uuid4()),
        name=p.stem,
        type="private",
        participants=participants,
        messages=messages,
    )
