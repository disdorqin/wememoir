from __future__ import annotations

from datetime import timedelta
from typing import List

from ..models import Message


def build_chapters(messages: list[Message], gap_days: int = 30) -> List[List[Message]]:
    """按消息间的空档时间把聊天记录划分成章节。"""
    msgs = sorted(messages, key=lambda m: m.timestamp)
    if not msgs:
        return []

    chapters: List[List[Message]] = [[msgs[0]]]
    for m in msgs[1:]:
        prev = chapters[-1][-1]
        if (m.timestamp - prev.timestamp) > timedelta(days=gap_days):
            chapters.append([m])
        else:
            chapters[-1].append(m)
    return chapters


def _avg_density(chapter: list[Message]) -> float:
    if len(chapter) <= 1:
        return float(len(chapter))
    span = (chapter[-1].timestamp - chapter[0].timestamp).total_seconds() or 1
    days = span / 86400
    return len(chapter) / max(days, 1)


def stage_name(index: int, chapter: list[Message], total: int) -> str:
    """根据章节位置和聊天密度返回关系阶段名称。"""
    density = _avg_density(chapter)
    span_days = (chapter[-1].timestamp - chapter[0].timestamp).days

    if total == 1:
        return "相识以来的日子"
    if index == 0:
        return "初识期"
    if index == total - 1:
        if density < 1:
            return "稳定期"
        return "重逢期" if total > 2 else "稳定期"
    if density >= 8:
        return "高频聊天期"
    if span_days > 90 and density < 1:
        return "冷淡期"
    return "转折期"
