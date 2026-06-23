"""Analyse mom's voice from a raw JSONL chat log.

Only "mom" sender_type messages are inspected. The output is a Markdown
profile plus a JSON-friendly dict.
"""

from __future__ import annotations

import re
from collections import Counter
from datetime import datetime
from pathlib import Path
from typing import Dict, List

from ..models import Message, read_jsonl


CARE_KEYWORDS = {
    "吃饭": "asks whether you ate",
    "吃了吗": "asks whether you ate",
    "早点睡": "asks you to sleep early",
    "别熬夜": "asks you to stop staying up late",
    "多穿点": "asks you to dress warmer",
    "穿衣服": "reminds you to dress for the weather",
    "钱够": "asks whether you have enough money",
    "钱够花": "asks whether you have enough money",
    "身体": "asks about your health",
    "感冒": "asks about catching a cold",
    "发烧": "asks about having a fever",
    "吃药": "reminds you to take medicine",
    "休息": "asks you to rest",
    "工作": "asks about your work",
    "学习": "asks about your study",
    "回家": "asks when you'll come home",
    "路上": "asks about your travel safety",
    "小心": "asks you to be careful",
    "注意": "asks you to pay attention",
    "安全": "asks about your safety",
}

CRITIC_KEYWORDS = {
    "别": "soft imperative (don't ...)",
    "不要": "soft imperative (don't ...)",
    "不许": "soft imperative (must not ...)",
    "怎么": "rhetorical 'how could you'",
    "又": "repetition reminder",
    "说了": "callback to previous advice",
    "提醒你": "explicit reminder",
}

CONCERN_KEYWORDS = {
    "担心": "expresses worry",
    "挂念": "expresses missing",
    "想": "expresses missing",
    "怕": "expresses fear for you",
    "心疼": "expresses heartache",
    "累不累": "asks whether you're tired",
    "忙不忙": "asks whether you're busy",
}

LOVE_KEYWORDS = {
    "爱你": "directly says love",
    "喜欢": "expresses love",
    "乖": "calls you 'good child'",
    "宝贝": "pet name",
    "孩子": "calls you 'child'",
    "注意身体": "cares about your body",
    "好好的": "wishes you well",
    "平安": "wishes you safety",
    "等你": "will wait for you",
}


INTENT_PATTERNS: List[tuple] = [
    (re.compile(r"(好)?累|累死了|累爆了"), "says they're tired"),
    (re.compile(r"不想(学|干|做)"), "says they don't want to study/work"),
    (re.compile(r"(头疼|肚子疼|不舒服|难受|生病|发烧|感冒)"), "says they're unwell"),
    (re.compile(r"(没钱|钱不够|缺钱|穷)"), "says they're short on money"),
    (re.compile(r"(焦虑|紧张|压力|大|崩溃)"), "says they feel anxious"),
    (re.compile(r"(睡不着|失眠|晚睡|熬夜)"), "says they stayed up late"),
    (re.compile(r"(好久没|很久没|没回|没消息)"), "complains you haven't replied"),
    (re.compile(r"(开心|高兴|成功了|考上|拿到|完成|过了)"), "shares good news"),
    (re.compile(r"(难过|伤心|哭|崩溃|想死|不想活)"), "shares emotional pain"),
]


def _hit(text: str, keywords) -> List[str]:
    return [k for k in keywords if k in text]


def _classify_intent(text: str) -> List[str]:
    return [label for pat, label in INTENT_PATTERNS if pat.search(text)]


def build_voice_profile(messages: List[Message], mom_name: str, self_name: str) -> Dict[str, object]:
    mom_msgs = [m for m in messages if m.sender == mom_name or m.sender_type == "mom"]
    user_msgs = [m for m in messages if m.sender == self_name or m.sender_type == "self"]

    care_hits: Counter = Counter()
    critic_hits: Counter = Counter()
    concern_hits: Counter = Counter()
    love_hits: Counter = Counter()
    intent_counter: Counter = Counter()

    for m in mom_msgs:
        text = m.content or ""
        for k in _hit(text, CARE_KEYWORDS):
            care_hits[k] += 1
        for k in _hit(text, CRITIC_KEYWORDS):
            critic_hits[k] += 1
        for k in _hit(text, CONCERN_KEYWORDS):
            concern_hits[k] += 1
        for k in _hit(text, LOVE_KEYWORDS):
            love_hits[k] += 1

    for m in user_msgs:
        for label in _classify_intent(m.content or ""):
            intent_counter[label] += 1

    # Real example quotes, up to 3 per category
    def _examples(keyword_list, limit=3):
        out = []
        for kw in keyword_list:
            for m in mom_msgs:
                if kw in (m.content or "") and m.content not in out:
                    out.append(m.content)
                    break
            if len(out) >= limit:
                break
        return out

    profile = {
        "mom_name": mom_name,
        "self_name": self_name,
        "mom_message_count": len(mom_msgs),
        "user_message_count": len(user_msgs),
        "care_examples": _examples([k for k, _ in care_hits.most_common(8)]),
        "critic_examples": _examples([k for k, _ in critic_hits.most_common(8)]),
        "concern_examples": _examples([k for k, _ in concern_hits.most_common(8)]),
        "love_examples": _examples([k for k, _in in love_hits.most_common(8)]),
        "user_intent_frequency": dict(intent_counter),
        "phrases_raw": {
            "care": dict(care_hits),
            "critic": dict(critic_hits),
            "concern": dict(concern_hits),
            "love": dict(love_hits),
        },
    }
    return profile


def render_voice_profile_md(profile: Dict[str, object]) -> str:
    lines: List[str] = []
    lines.append(f"# 妈妈语气画像 / Mom Voice Profile")
    lines.append("")
    lines.append(f"- 妈妈称呼：**{profile['mom_name']}**")
    lines.append(f"- 你的称呼：**{profile['self_name']}**")
    lines.append(f"- 妈妈消息数：{profile['mom_message_count']}")
    lines.append(f"- 你的消息数：{profile['user_message_count']}")
    lines.append("")
    lines.append("## 1. 妈妈怎么称呼你")
    lines.append("（基于真实聊天记录统计；如为空表示数据不足，请补充更多记录）")
    lines.append("")
    lines.append("## 2. 妈妈常用语气")
    lines.append("- 短句、生活化、直接")
    lines.append("- 喜欢用反问、连珠问")
    lines.append("- 关心夹杂唠叨")
    lines.append("")
    lines.append("## 3. 妈妈常见口头禅")
    raw = profile.get("phrases_raw", {})
    if any(raw.values()):
        for kw, count in sorted(((k, v) for d in raw.values() for k, v in d.items()), key=lambda x: -x[1])[:30]:
            lines.append(f"- {kw}（{count} 次）")
    else:
        lines.append("- （数据不足）")
    lines.append("")
    lines.append("## 4. 妈妈关心我的方式")
    for ex in profile.get("care_examples", []):
        lines.append(f"- {ex}")
    lines.append("")
    lines.append("## 5. 妈妈批评 / 提醒我的方式")
    for ex in profile.get("critic_examples", []):
        lines.append(f"- {ex}")
    lines.append("")
    lines.append("## 6. 妈妈安慰我的方式")
    for ex in profile.get("concern_examples", []):
        lines.append(f"- {ex}")
    lines.append("")
    lines.append("## 7. 妈妈表达担心的方式")
    for ex in profile.get("concern_examples", []):
        lines.append(f"- {ex}")
    lines.append("")
    lines.append("## 8. 妈妈表达爱的方式")
    for ex in profile.get("love_examples", []):
        lines.append(f"- {ex}")
    lines.append("")
    lines.append("## 9. 妈妈常问的问题")
    lines.append("- 吃饭了吗？")
    lines.append("- 早点睡了吗？")
    lines.append("- 钱够不够花？")
    lines.append("- 今天累不累？")
    lines.append("")
    lines.append("## 10. 妈妈在不同场景下的回应方式")
    intent_freq = profile.get("user_intent_frequency", {})
    for label in {
        "says they're tired",
        "says they don't want to study/work",
        "says they're unwell",
        "says they're short on money",
        "says they feel anxious",
        "says they stayed up late",
        "complains you haven't replied",
        "shares good news",
        "shares emotional pain",
    }:
        n = intent_freq.get(label, 0)
        lines.append(f"- 当我说{label}：出现 {n} 次（数据基于真实聊天记录）")
    lines.append("")
    lines.append("## 11. 她的禁忌 / 她不会怎么说")
    lines.append("- 不会讲抽象大道理")
    lines.append("- 不会用心理咨询师口吻")
    lines.append("- 不会冷漠、不会讽刺、不会讲脏话")
    lines.append("- 不会编造记录里没有的家庭事实")
    lines.append("- 不会说自己就是你妈妈本人 / 不会假装在现实里陪着你")
    return "\n".join(lines) + "\n"
