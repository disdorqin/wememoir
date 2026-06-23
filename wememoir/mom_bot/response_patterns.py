"""Map user intent to mom's real response style."""

from __future__ import annotations

import re
from typing import Dict, List

from ..models import Message


INTENT_RULES_INTERNAL: List[tuple] = [
    (re.compile(r"好?累|累死了|累爆"), "user_is_tired"),
    (re.compile(r"不想(学|干|做)"), "user_does_not_want_to_study_or_work"),
    (re.compile(r"(头疼|肚子疼|不舒服|难受|生病|发烧|感冒)"), "user_is_unwell"),
    (re.compile(r"(没钱|钱不够|缺钱)"), "user_is_short_on_money"),
    (re.compile(r"(焦虑|紧张|压力大|崩溃)"), "user_is_anxious"),
    (re.compile(r"(睡不着|失眠|晚睡|熬夜)"), "user_stayed_up_late"),
    (re.compile(r"(好久没|很久没|没回|没消息)"), "user_did_not_reply"),
    (re.compile(r"(开心|高兴|成功了|考上|拿到|完成|过了)"), "user_shares_good_news"),
    (re.compile(r"(难过|伤心|哭|崩溃|想死|不想活)"), "user_is_upset"),
]


# Pure intent labels, JSON-serialisable. Kept separate from the regex tuples
# so ``json.dumps(patterns)`` does not try to serialise compiled regex objects.
INTENT_LABELS: List[str] = [label for _, label in INTENT_RULES_INTERNAL]
INTENT_RULES = INTENT_RULES_INTERNAL  # backwards-compatible alias


TEMPLATE = {
    "user_is_tired": "累了就早点睡，别硬撑。",
    "user_does_not_want_to_study_or_work": "不想学就不想学，歇一歇再弄。",
    "user_is_unwell": "先喝点水，吃不吃药看情况。",
    "user_is_short_on_money": "钱不够和家里说，别委屈自己。",
    "user_is_anxious": "别想太多，一件一件来。",
    "user_stayed_up_late": "怎么又熬夜？赶紧睡。",
    "user_did_not_reply": "怎么不回消息，是不是忙？",
    "user_shares_good_news": "真好，我就知道你行。",
    "user_is_upset": "怎么了？和妈妈说说。",
}


def _classify(text: str) -> List[str]:
    return [intent for pat, intent in INTENT_RULES if pat.search(text or "")]


def extract_response_patterns(
    messages: List[Message], mom_name: str, self_name: str
) -> Dict[str, object]:
    """Walk user-then-mom message pairs and record real examples."""
    msgs = sorted(messages, key=lambda m: m.timestamp)
    buckets: Dict[str, List[Dict[str, str]]] = {label: [] for _, label in INTENT_RULES_INTERNAL}

    last_user_intents: List[str] = []
    last_user_text = ""
    for m in msgs:
        if m.sender == self_name or m.sender_type == "self":
            last_user_text = m.content or ""
            last_user_intents = _classify(last_user_text)
            continue
        if (m.sender == mom_name or m.sender_type == "mom") and last_user_intents:
            for intent in last_user_intents:
                buckets[intent].append(
                    {
                        "user": last_user_text,
                        "mom": m.content or "",
                        "timestamp": m.timestamp.isoformat()
                        if hasattr(m.timestamp, "isoformat")
                        else str(m.timestamp),
                    }
                )
            last_user_intents = []

    patterns: List[Dict[str, object]] = []
    for _, intent in INTENT_RULES_INTERNAL:
        examples = buckets.get(intent, [])[:5]
        patterns.append(
            {
                "user_intent": intent,
                "mom_response_style": _describe_style(intent),
                "real_examples": examples,
                "suggested_bot_response_template": TEMPLATE.get(intent, ""),
            }
        )
    return {"mom_name": mom_name, "self_name": self_name, "patterns": patterns}


def _describe_style(intent: str) -> str:
    return {
        "user_is_tired": "短句，劝你早点睡，关心你的身体",
        "user_does_not_want_to_study_or_work": "不会硬逼你，会让你先歇一歇",
        "user_is_unwell": "直接问你哪里不舒服，让你先喝水/吃药",
        "user_is_short_on_money": "担心你饿着，让你开口和家里说",
        "user_is_anxious": "让你别想太多，一件一件来",
        "user_stayed_up_late": "小抱怨 + 让你赶紧睡",
        "user_did_not_reply": "略带担心地问你在不在",
        "user_shares_good_news": "替你高兴，但很快又叮嘱你别骄傲",
        "user_is_upset": "让你说出来，不评价不打断",
    }.get(intent, "关心但不啰嗦")


def render_response_patterns_md(patterns: Dict[str, object]) -> str:
    lines = ["# 妈妈回应模式 / Mom Response Patterns", ""]
    for p in patterns.get("patterns", []):
        lines.append(f"## {p['user_intent']}")
        lines.append(f"- 妈妈风格：{p['mom_response_style']}")
        if p.get("suggested_bot_response_template"):
            lines.append(f"- Bot 模板：{p['suggested_bot_response_template']}")
        for ex in p.get("real_examples", []):
            lines.append(f"  - 我：{ex['user']}")
            lines.append(f"    妈：{ex['mom']}")
        lines.append("")
    return "\n".join(lines) + "\n"
