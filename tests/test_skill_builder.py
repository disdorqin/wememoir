from __future__ import annotations

from datetime import datetime

from wememoir.models import Conversation, Message
from wememoir.skills import build_skill


def _conv():
    messages = [
        Message(
            id="m1",
            timestamp=datetime(2023, 1, 1, 10, 0),
            sender="Me",
            sender_type="self",
            content="今天天气真好，我们出去走走吧",
            raw_content="今天天气真好，我们出去走走吧",
        ),
        Message(
            id="m2",
            timestamp=datetime(2023, 1, 1, 10, 1),
            sender="Alice",
            content="好啊，几点见？",
            raw_content="好啊，几点见？",
        ),
    ]
    return Conversation(
        id="c1",
        name="Alice",
        type="private",
        participants=["Me", "Alice"],
        messages=messages,
    )


def test_build_skill_codex(tmp_path):
    conv = _conv()
    out = tmp_path / "AGENTS.md"
    text = build_skill(conv, skill_type="contact", target="codex", out_path=str(out))
    assert out.exists()
    assert "AGENTS" in text or "Agent" in text
    assert "使用场景" in text or "Role" in text
    assert "隐私边界" in text or "Constraints" in text


def test_build_skill_generic(tmp_path):
    conv = _conv()
    out = tmp_path / "SKILL.md"
    text = build_skill(conv, skill_type="self", target="generic", out_path=str(out))
    assert out.exists()
    assert "我的表达风格" in text
    assert "可调用的本地文件说明" in text
