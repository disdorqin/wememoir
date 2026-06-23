"""The mom voice profile must retain real phrases from the chat log."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path

from wememoir.models import Message, write_jsonl
from wememoir.mom_bot import build_mom_bot


def _msgs():
    return [
        Message("a1", datetime(2023, 5, 1, 10, 0, 0), "妈妈", "mom", "text", "吃饭了吗", "吃饭了吗", "wechat_pc", "妈妈"),
        Message("a2", datetime(2023, 5, 1, 10, 1, 0), "我", "self", "text", "还没", "还没", "wechat_pc", "妈妈"),
        Message("a3", datetime(2023, 5, 2, 22, 0, 0), "妈妈", "mom", "text", "早点睡，别熬夜", "早点睡，别熬夜", "wechat_pc", "妈妈"),
        Message("a4", datetime(2023, 5, 3, 23, 0, 0), "我", "self", "text", "今天又加班", "今天又加班", "wechat_pc", "妈妈"),
        Message("a5", datetime(2023, 5, 4, 8, 0, 0), "妈妈", "mom", "text", "记得吃早饭", "记得吃早饭", "wechat_pc", "妈妈"),
    ]


def test_profile_keeps_real_phrases(tmp_path: Path):
    src = tmp_path / "raw.jsonl"
    write_jsonl(_msgs(), str(src))
    out = tmp_path / "bot"
    build_mom_bot(raw_path=str(src), out_dir=str(out), self_name="我", mom_name="妈妈")
    profile = (out / "profile" / "mom_voice_profile.md").read_text(encoding="utf-8")
    assert "吃饭了吗" in profile
    assert "早点睡" in profile
    assert "别熬夜" in profile


def test_phrases_json_has_real_quotes(tmp_path: Path):
    src = tmp_path / "raw.jsonl"
    write_jsonl(_msgs(), str(src))
    out = tmp_path / "bot"
    build_mom_bot(raw_path=str(src), out_dir=str(out), self_name="我", mom_name="妈妈")
    import json
    phrases = json.loads((out / "profile" / "mom_phrases.json").read_text(encoding="utf-8"))
    assert phrases["total_unique"] >= 3
    texts = {p["phrase"] for p in phrases["phrases"]}
    assert "吃饭了吗" in texts
    assert "早点睡，别熬夜" in texts


def test_response_patterns_capture_user_intent(tmp_path: Path):
    src = tmp_path / "raw.jsonl"
    write_jsonl(_msgs(), str(src))
    out = tmp_path / "bot"
    build_mom_bot(raw_path=str(src), out_dir=str(out), self_name="我", mom_name="妈妈")
    import json
    patterns = json.loads((out / "profile" / "mom_response_patterns.json").read_text(encoding="utf-8"))
    intents = {p["user_intent"] for p in patterns["patterns"]}
    # user_stayed_up_late + user_is_tired both detectable in the sample
    assert "user_stayed_up_late" in intents
    assert "user_is_tired" in intents
