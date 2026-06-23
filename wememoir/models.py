from __future__ import annotations

import uuid
from dataclasses import asdict, dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional


SENDER_SELF = "self"
SENDER_MOM = "mom"
SENDER_OTHER = "other"
SENDER_SYSTEM = "system"
SENDER_UNKNOWN = "unknown"

VALID_SENDER_TYPES = {SENDER_SELF, SENDER_MOM, SENDER_OTHER, SENDER_SYSTEM, SENDER_UNKNOWN}

MSG_TEXT = "text"
MSG_IMAGE = "image"
MSG_VOICE = "voice"
MSG_VIDEO = "video"
MSG_FILE = "file"
MSG_SYSTEM = "system"
MSG_REDPACKET = "redpacket"
MSG_TRANSFER = "transfer"
MSG_EMOJI = "emoji"
MSG_RECALL = "recall"
MSG_UNKNOWN = "unknown"

VALID_MESSAGE_TYPES = {
    MSG_TEXT, MSG_IMAGE, MSG_VOICE, MSG_VIDEO, MSG_FILE,
    MSG_SYSTEM, MSG_REDPACKET, MSG_TRANSFER, MSG_EMOJI, MSG_RECALL, MSG_UNKNOWN,
}


@dataclass
class Message:
    id: str
    timestamp: datetime
    sender: str
    sender_type: str = SENDER_UNKNOWN
    message_type: str = MSG_UNKNOWN
    content: str = ""
    raw_content: str = ""
    source: str = "unknown"
    conversation_name: str = ""

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data["timestamp"] = self.timestamp.isoformat()
        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Message":
        payload = dict(data)
        ts = payload.get("timestamp")
        if isinstance(ts, str):
            try:
                ts = datetime.fromisoformat(ts)
            except ValueError:
                ts = datetime.utcnow()
        elif not isinstance(ts, datetime):
            ts = datetime.utcnow()
        payload["timestamp"] = ts

        if payload.get("sender_type") not in VALID_SENDER_TYPES:
            payload["sender_type"] = SENDER_UNKNOWN
        if payload.get("message_type") not in VALID_MESSAGE_TYPES:
            payload["message_type"] = MSG_UNKNOWN
        return cls(**payload)


@dataclass
class Conversation:
    id: str
    name: str
    type: str = "private"
    participants: List[str] = field(default_factory=list)
    messages: List[Message] = field(default_factory=list)
    source: str = "unknown"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "type": self.type,
            "participants": self.participants,
            "source": self.source,
            "messages": [m.to_dict() for m in self.messages],
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Conversation":
        messages = [Message.from_dict(m) for m in data.get("messages", [])]
        return cls(
            id=data.get("id", str(uuid.uuid4())),
            name=data.get("name", "Imported Chat"),
            type=data.get("type", "private"),
            participants=list(data.get("participants", [])),
            messages=messages,
            source=data.get("source", "unknown"),
        )


def read_jsonl(path: str) -> List[Message]:
    """Read a JSONL file as raw messages. NEVER filters or drops anything."""
    import json
    from pathlib import Path

    messages: List[Message] = []
    text = Path(path).read_text(encoding="utf-8")
    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue
        payload = json.loads(line)
        messages.append(Message.from_dict(payload))
    return messages


def write_jsonl(messages: List[Message], path: str) -> None:
    """Write messages as JSONL. Preserves every message verbatim."""
    import json
    from pathlib import Path

    lines = [json.dumps(m.to_dict(), ensure_ascii=False) for m in messages]
    Path(path).write_text("\n".join(lines) + "\n", encoding="utf-8")
