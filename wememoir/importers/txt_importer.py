from __future__ import annotations

import re
import uuid
from datetime import datetime
from pathlib import Path

from dateutil import parser as date_parser

from ..models import Conversation, Message


_LINE_PATTERNS = [
    re.compile(
        r"^(?P<ts>\d{4}[-/]\d{2}[-/]\d{2}\s+\d{1,2}:\d{2}(?::\d{2})?)\s+(?P<sender>[^:]+?)(?P<sep>:|：)\s*(?P<content>.*)$"
    ),
    re.compile(r"^\[(?P<ts>\d{4}[-/]\d{2}[-/]\d{2}\s+\d{1,2}:\d{2}(?::\d{2})?)\]\s*(?P<sender>[^\]]+)\]\s*(?P<content>.*)$"),
    re.compile(r"^\[(?P<sender>[^\]]+)\]\s*(?P<content>.*)$"),
]

_PLACEHOLDERS = {"[图片]", "[语音]", "[视频]", "[红包]", "[转账]", "[动画表情]", "[表情包]", "[文件]", "[位置]", "[链接]"}


def _parse_timestamp(value: str | None, fallback: datetime | None = None) -> datetime:
    if not value:
        return fallback or datetime.utcnow()
    try:
        return date_parser.parse(value.strip(), fuzzy=True)
    except Exception:
        for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d %H:%M", "%Y/%m/%d %H:%M:%S", "%Y/%m/%d %H:%M"):
            try:
                return datetime.strptime(value.strip(), fmt)
            except Exception:
                continue
        return fallback or datetime.utcnow()


def _is_system(content: str, sender: str) -> bool:
    text = content.strip()
    if sender.strip() == "系统":
        return True
    if "撤回了一条消息" in text or "消息已撤回" in text:
        return True
    if text.startswith(("你邀请", "邀请你", "加入了群聊", "移出了群聊", "修改群名")):
        return True
    return False


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


def parse_text(text: str) -> Conversation:
    messages: list[Message] = []
    participants: set[str] = set()
    last_ts: datetime | None = None

    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line:
            continue

        matched = False
        for pat in _LINE_PATTERNS:
            m = pat.match(line)
            if not m:
                continue
            gd = m.groupdict()
            ts_str = gd.get("ts")
            sender = gd.get("sender", "").strip() or "unknown"
            content = gd.get("content", "").strip()
            ts = _parse_timestamp(ts_str, fallback=last_ts)
            last_ts = ts

            msg_type = "system" if _is_system(content, sender) else _classify_message_type(content)
            participants.add(sender)
            messages.append(
                Message(
                    id=str(uuid.uuid4()),
                    timestamp=ts,
                    sender=sender,
                    sender_type="other",
                    message_type=msg_type,
                    content=content,
                    raw_content=content,
                )
            )
            matched = True
            break

        if not matched and messages:
            messages[-1].content += "\n" + line
            messages[-1].raw_content += "\n" + line

    return Conversation(
        id=str(uuid.uuid4()),
        name="Imported Chat",
        type="private",
        participants=sorted(participants),
        messages=messages,
    )


def import_txt(path: str) -> Conversation:
    text = Path(path).read_text(encoding="utf-8-sig")
    conversation = parse_text(text)
    conversation.name = Path(path).stem
    return conversation
