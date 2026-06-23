"""Build a memory map of shared events between you and mom."""

from __future__ import annotations

from collections import defaultdict
from datetime import datetime
from typing import Dict, List

from ..models import Message


_KEYWORDS = {
    "吃饭": "meal",
    "生日": "birthday",
    "过年": "new year",
    "中秋": "mid-autumn",
    "端午": "dragon boat",
    "医院": "hospital",
    "病": "illness",
    "发烧": "fever",
    "毕业": "graduation",
    "工作": "work",
    "面试": "interview",
    "回家": "going home",
    "哭": "crying",
    "开心": "happy moment",
    "难过": "sad moment",
    "吵架": "argument",
    "想": "missing",
    "等你": "waiting",
    "钱": "money",
    "学校": "school",
    "考试": "exam",
}


def _events_for(text: str) -> List[str]:
    if not text:
        return []
    return [label for kw, label in _KEYWORDS.items() if kw in text]


def build_memory_map(messages: List[Message], mom_name: str, self_name: str) -> Dict[str, object]:
    msgs = sorted(messages, key=lambda m: m.timestamp)
    grouped: Dict[str, List[Message]] = defaultdict(list)
    for m in msgs:
        for label in _events_for(m.content or ""):
            grouped[label].append(m)

    events = []
    for label, ms in grouped.items():
        first = min(ms, key=lambda x: x.timestamp)
        last = max(ms, key=lambda x: x.timestamp)
        events.append(
            {
                "label": label,
                "first_seen": first.timestamp.isoformat()
                if hasattr(first.timestamp, "isoformat")
                else str(first.timestamp),
                "last_seen": last.timestamp.isoformat()
                if hasattr(last.timestamp, "isoformat")
                else str(last.timestamp),
                "count": len(ms),
                "example_quote": (first.content or "")[:120],
            }
        )
    events.sort(key=lambda e: e["first_seen"])
    return {"mom_name": mom_name, "self_name": self_name, "events": events}


def render_memory_map_md(memory: Dict[str, object]) -> str:
    lines = ["# 共同记忆地图 / Shared Memory Map", ""]
    if not memory.get("events"):
        lines.append("（暂无足够信息；导入更多聊天记录后会自动丰富。）")
        return "\n".join(lines) + "\n"
    for e in memory["events"]:
        lines.append(f"## {e['label']}（出现 {e['count']} 次）")
        lines.append(f"- 首次：{e['first_seen']}")
        lines.append(f"- 最近：{e['last_seen']}")
        if e.get("example_quote"):
            lines.append(f"- 代表性原话：{e['example_quote']}")
        lines.append("")
    return "\n".join(lines) + "\n"
