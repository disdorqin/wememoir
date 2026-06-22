from __future__ import annotations

import csv
import uuid
from datetime import datetime
from pathlib import Path

from dateutil import parser as date_parser

from ..models import Conversation, Message


def _classify_message_type(content: str) -> str:
    text = content.strip()
    if text == "[图片]":
        return "image"
    if text == "[语音]":
        return "audio"
    if text == "[视频]":
        return "video"
    if text == "[红包]":
        return "redpacket"
    if text == "[转账]":
        return "transfer"
    return "text"


def _parse_timestamp(value: str) -> datetime:
    value = value.strip()
    try:
        return date_parser.parse(value, fuzzy=True)
    except Exception:
        for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d %H:%M", "%Y/%m/%d %H:%M:%S", "%Y/%m/%d %H:%M"):
            try:
                return datetime.strptime(value, fmt)
            except Exception:
                continue
        return datetime.utcnow()


def import_csv(path: str) -> Conversation:
    p = Path(path)
    messages: list[Message] = []
    participants: set[str] = set()

    with open(p, encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        if reader.fieldnames is None:
            raise ValueError("CSV has no header")

        fields = [fn.lower().strip() for fn in reader.fieldnames]

        def col(*names: str):
            for name in names:
                if name in fields:
                    return reader.fieldnames[fields.index(name)]
            return None

        ts_col = col("timestamp", "time", "date", "datetime", "时间", "日期")
        sender_col = col("sender", "from", "name", "发送者", "昵称")
        content_col = col("content", "message", "text", "msg", "内容", "消息")
        type_col = col("message_type", "type", "类型")

        if not all((ts_col, sender_col, content_col)):
            raise ValueError("CSV must contain timestamp, sender and content columns")

        for i, row in enumerate(reader):
            ts = _parse_timestamp(row[ts_col])
            sender = row[sender_col].strip() or "unknown"
            content = row[content_col]
            msg_type = row[type_col].strip().lower() if type_col and row[type_col] else _classify_message_type(content)
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

    return Conversation(
        id=str(uuid.uuid4()),
        name=p.stem,
        type="private",
        participants=sorted(participants),
        messages=messages,
    )
