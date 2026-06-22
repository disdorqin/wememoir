from __future__ import annotations

import uuid
from dataclasses import asdict, dataclass, field
from datetime import datetime
from typing import Any, Dict, List


@dataclass
class Message:
    id: str
    timestamp: datetime
    sender: str
    sender_type: str = "other"
    message_type: str = "text"
    content: str = ""
    raw_content: str = ""

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data["timestamp"] = self.timestamp.isoformat()
        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Message":
        payload = dict(data)
        ts = payload.get("timestamp")
        if isinstance(ts, str):
            ts = datetime.fromisoformat(ts)
        elif not isinstance(ts, datetime):
            ts = datetime.utcnow()
        payload["timestamp"] = ts
        return cls(**payload)


@dataclass
class Conversation:
    id: str
    name: str
    type: str = "private"
    participants: List[str] = field(default_factory=list)
    messages: List[Message] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "type": self.type,
            "participants": self.participants,
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
        )
