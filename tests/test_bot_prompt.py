"""The system prompt must contain hard guardrails and never claim to BE mom."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path

from wememoir.models import Message, write_jsonl
from wememoir.mom_bot import build_mom_bot


def _msgs():
    return [
        Message("a1", datetime(2023, 5, 1, 10, 0, 0), "妈妈", "mom", "text", "吃饭了吗", "吃饭了吗", "wechat_pc", "妈妈"),
        Message("a2", datetime(2023, 5, 1, 10, 1, 0), "我", "self", "text", "还没", "还没", "wechat_pc", "妈妈"),
    ]


def test_prompt_has_anti_fabrication_guardrail(tmp_path: Path):
    src = tmp_path / "raw.jsonl"
    write_jsonl(_msgs(), str(src))
    out = tmp_path / "bot"
    build_mom_bot(raw_path=str(src), out_dir=str(out), self_name="我", mom_name="妈妈")
    prompt = (out / "bot" / "MOM_BOT_SYSTEM_PROMPT.md").read_text(encoding="utf-8")
    assert "不要编造聊天记录里没有的具体事实" in prompt
    assert "优先使用聊天记录中真实出现过的表达方式" in prompt


def test_prompt_does_not_pretend_to_be_mom(tmp_path: Path):
    src = tmp_path / "raw.jsonl"
    write_jsonl(_msgs(), str(src))
    out = tmp_path / "bot"
    build_mom_bot(raw_path=str(src), out_dir=str(out), self_name="我", mom_name="妈妈")
    prompt = (out / "bot" / "MOM_BOT_SYSTEM_PROMPT.md").read_text(encoding="utf-8")
    # Must not say "I am your mother" / "I am your real mom"
    assert "我就是你妈妈本人" not in prompt
    assert "我是你亲生母亲" not in prompt
    # The phrase must appear in the guardrail section, not as a claim
    assert "不要声称自己正在现实里陪着用户" in prompt


def test_prompt_routes_crisis_to_real_people(tmp_path: Path):
    src = tmp_path / "raw.jsonl"
    write_jsonl(_msgs(), str(src))
    out = tmp_path / "bot"
    build_mom_bot(raw_path=str(src), out_dir=str(out), self_name="我", mom_name="妈妈")
    prompt = (out / "bot" / "MOM_BOT_SYSTEM_PROMPT.md").read_text(encoding="utf-8")
    assert "心理援助热线" in prompt or "亲人朋友" in prompt
