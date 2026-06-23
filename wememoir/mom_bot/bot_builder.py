"""Top-level orchestration for ``wememoir mom-bot``."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List

from ..models import Message, read_jsonl, write_jsonl
from .memory_mapper import build_memory_map, render_memory_map_md
from .phrase_extractor import extract_phrases
from .prompt_builder import build_system_prompt
from .response_patterns import extract_response_patterns, render_response_patterns_md
from .voice_analyzer import build_voice_profile, render_voice_profile_md


def _write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def _raw_excerpt(messages: List[Message], max_lines: int = 60) -> str:
    out: List[str] = []
    for m in messages[:max_lines]:
        ts = m.timestamp.isoformat() if hasattr(m.timestamp, "isoformat") else str(m.timestamp)
        out.append(f"[{ts}] {m.sender} ({m.sender_type}/{m.message_type}): {m.content}")
    return "\n".join(out)


def build_character_card(profile, phrases, response_patterns, mom_name, self_name) -> Dict[str, object]:
    return {
        "name": "妈妈风格陪伴 Bot",
        "version": "0.2.0",
        "description": (
            "A comfort companion that imitates the tone of the user's own mother, "
            "based on their real chat history. NOT the real mother. See MOM_BOT_SYSTEM_PROMPT.md."
        ),
        "persona": {
            "based_on_mom_name": mom_name,
            "self_name": self_name,
        },
        "system_prompt_file": "MOM_BOT_SYSTEM_PROMPT.md",
        "voice_profile_file": "profile/mom_voice_profile.md",
        "phrases_file": "profile/mom_phrases.json",
        "response_patterns_file": "profile/mom_response_patterns.json",
        "memory_map_file": "profile/mom_memory_map.md",
        "raw_excerpt_file": "raw/mom_chat_full.md",
        "guardrails": [
            "never claim to be the real mother",
            "never claim to be physically present",
            "never fabricate facts not in the chat log",
            "route crisis to real people",
        ],
        "stats": {
            "mom_messages": profile.get("mom_message_count", 0),
            "user_messages": profile.get("user_message_count", 0),
            "phrases": phrases.get("total_unique", 0),
        },
    }


def build_mom_bot(
    raw_path: str,
    out_dir: str,
    self_name: str = "我",
    mom_name: str = "妈妈",
) -> Dict[str, object]:
    """Build the entire mom-bot data package on disk.

    The raw JSONL is copied verbatim into ``out_dir/raw/`` and is NEVER
    modified.
    """
    src = Path(raw_path)
    out = Path(out_dir)

    messages = read_jsonl(str(src))
    messages.sort(key=lambda m: m.timestamp)

    raw_dir = out / "raw"
    profile_dir = out / "profile"
    bot_dir = out / "bot"
    raw_dir.mkdir(parents=True, exist_ok=True)
    profile_dir.mkdir(parents=True, exist_ok=True)
    bot_dir.mkdir(parents=True, exist_ok=True)

    # 1. Verbatim raw copy
    write_jsonl(messages, str(raw_dir / "mom_chat_full.jsonl"))
    # 2. Verbatim human-readable mirror
    md_lines = ["# 妈妈聊天全文 / Raw Chat (verbatim)\n"]
    for m in messages:
        ts = m.timestamp.isoformat() if hasattr(m.timestamp, "isoformat") else str(m.timestamp)
        md_lines.append(f"- [{ts}] **{m.sender}** ({m.sender_type}/{m.message_type}): {m.content}")
    _write(raw_dir / "mom_chat_full.md", "\n".join(md_lines) + "\n")

    # 3. Profile
    profile = build_voice_profile(messages, mom_name=mom_name, self_name=self_name)
    _write(profile_dir / "mom_voice_profile.md", render_voice_profile_md(profile))

    phrases = extract_phrases(messages, mom_name=mom_name)
    _write(profile_dir / "mom_phrases.json", json.dumps(phrases, ensure_ascii=False, indent=2))

    patterns = extract_response_patterns(messages, mom_name=mom_name, self_name=self_name)
    _write(
        profile_dir / "mom_response_patterns.json",
        json.dumps(patterns, ensure_ascii=False, indent=2),
    )
    _write(profile_dir / "mom_response_patterns.md", render_response_patterns_md(patterns))

    memory = build_memory_map(messages, mom_name=mom_name, self_name=self_name)
    _write(profile_dir / "mom_memory_map.md", render_memory_map_md(memory))

    # 4. Bot files
    profile_md = (profile_dir / "mom_voice_profile.md").read_text(encoding="utf-8")
    memory_md = (profile_dir / "mom_memory_map.md").read_text(encoding="utf-8")
    raw_excerpt = _raw_excerpt(messages)
    system_prompt = build_system_prompt(
        mom_name=mom_name,
        self_name=self_name,
        profile_md=profile_md,
        phrases_json=phrases,
        response_patterns_json=patterns,
        memory_md=memory_md,
        raw_excerpt=raw_excerpt,
    )
    _write(bot_dir / "MOM_BOT_SYSTEM_PROMPT.md", system_prompt)

    card = build_character_card(profile, phrases, patterns, mom_name, self_name)
    _write(bot_dir / "character_card.json", json.dumps(card, ensure_ascii=False, indent=2))

    agents_md = (
        f"# AGENTS.md / Mom-style Comfort Bot\n\n"
        f"本目录是 WeMemoir 生成的妈妈风格陪伴 Bot 数据包。\n\n"
        f"- 仅在本地运行；不要把聊天记录发到云端，除非用户明确同意。\n"
        f"- 使用前请先阅读 `bot/MOM_BOT_SYSTEM_PROMPT.md` 了解所有安全边界。\n"
        f"- 真实聊天原文：`raw/mom_chat_full.jsonl`（不要修改、删除或伪造）。\n"
        f"- 妈妈语气画像：`profile/mom_voice_profile.md`。\n"
        f"- 共同记忆：`profile/mom_memory_map.md`。\n"
        f"- 回应模式：`profile/mom_response_patterns.json`。\n"
    )
    _write(bot_dir / "AGENTS.md", agents_md)

    return {
        "ok": True,
        "out_dir": str(out),
        "raw_messages": len(messages),
        "raw_path": str(raw_dir / "mom_chat_full.jsonl"),
        "system_prompt_path": str(bot_dir / "MOM_BOT_SYSTEM_PROMPT.md"),
        "character_card_path": str(bot_dir / "character_card.json"),
        "mom_messages": profile.get("mom_message_count", 0),
        "user_messages": profile.get("user_message_count", 0),
    }
