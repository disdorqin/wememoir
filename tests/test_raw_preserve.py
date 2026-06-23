"""The raw chat log must be preserved verbatim through `mom-bot`."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from wememoir.models import Message, read_jsonl, write_jsonl
from wememoir.mom_bot import build_mom_bot


EXAMPLES = Path(__file__).resolve().parent.parent / "examples" / "mom_sample.jsonl"


def _build_varied_messages():
    return [
        Message(
            id=f"v{i}",
            timestamp=__import__("datetime").datetime(2024, 1, 1, 10, 0, i),
            sender="我" if i % 2 else "妈妈",
            sender_type="self" if i % 2 else "mom",
            message_type=t,
            content=c,
            raw_content=c,
            source="wechat_pc",
            conversation_name="妈妈",
        )
        for i, (t, c) in enumerate(
            [
                ("text", "妈我今天好累"),
                ("text", "累了就早点睡"),
                ("system", "你已添加了妈妈"),
                ("emoji", "[表情] 比心"),
                ("recall", "你撤回了一条消息"),
                ("redpacket", "[红包] 恭喜发财"),
                ("image", "[图片] FileStorage/x.jpg"),
                ("voice", "[语音] FileStorage/y.dat"),
                ("video", "[视频] FileStorage/z.mp4"),
                ("transfer", "[转账] 100.00"),
            ]
        )
    ]


def test_raw_preserved_after_mom_bot(tmp_path: Path):
    src = tmp_path / "raw.jsonl"
    msgs = _build_varied_messages()
    write_jsonl(msgs, str(src))
    out = tmp_path / "bot"
    build_mom_bot(raw_path=str(src), out_dir=str(out), self_name="我", mom_name="妈妈")

    raw = read_jsonl(str(out / "raw" / "mom_chat_full.jsonl"))
    assert len(raw) == len(msgs), "raw messages must be preserved 1:1"
    assert [m.id for m in raw] == [m.id for m in msgs], "message order and ids must match"
    assert {m.message_type for m in raw} >= {
        "text", "system", "emoji", "recall", "redpacket", "image", "voice", "video", "transfer"
    }


def test_system_recall_redpacket_placeholders_kept(tmp_path: Path):
    src = tmp_path / "raw.jsonl"
    msgs = _build_varied_messages()
    write_jsonl(msgs, str(src))
    out = tmp_path / "bot"
    build_mom_bot(raw_path=str(src), out_dir=str(out), self_name="我", mom_name="妈妈")
    raw = read_jsonl(str(out / "raw" / "mom_chat_full.jsonl"))
    types = [m.message_type for m in raw]
    assert "system" in types
    assert "recall" in types
    assert "redpacket" in types
    assert "image" in types
    assert "voice" in types


def test_mom_bot_summary_fields(tmp_path: Path):
    src = tmp_path / "raw.jsonl"
    msgs = _build_varied_messages()
    write_jsonl(msgs, str(src))
    out = tmp_path / "bot"
    summary = build_mom_bot(raw_path=str(src), out_dir=str(out), self_name="我", mom_name="妈妈")
    assert summary["ok"] is True
    assert summary["raw_messages"] == 10
    assert (out / "bot" / "MOM_BOT_SYSTEM_PROMPT.md").exists()
    assert (out / "bot" / "character_card.json").exists()
    assert (out / "raw" / "mom_chat_full.md").exists()
