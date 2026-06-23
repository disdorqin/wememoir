from __future__ import annotations

import re
from collections import Counter
from pathlib import Path
from typing import List

from ..models import Message
from .timeline import build_timeline


def generate_highlights(messages: list[Message], path: str | None = None) -> str:
    msgs = build_timeline(messages)
    lines: List[str] = ["# 聊天 Highlights", ""]

    if not msgs:
        lines.append("暂无内容。")
        text = "\n".join(lines)
        if path:
            Path(path).write_text(text, encoding="utf-8")
        return text

    # 第一次聊天
    first = msgs[0]
    lines.append(f"- **第一次聊天**：{first.timestamp.strftime('%Y-%m-%d %H:%M')} [{first.sender}] {first.content}")

    # 最长连续聊天
    streak_start = streak_end = msgs[0]
    max_start = max_end = msgs[0]
    max_len = 1
    cur_len = 1
    for i in range(1, len(msgs)):
        if (msgs[i].timestamp - msgs[i - 1].timestamp).total_seconds() <= 1800:
            cur_len += 1
            streak_end = msgs[i]
        else:
            if cur_len > max_len:
                max_len = cur_len
                max_start, max_end = streak_start, streak_end
            streak_start = streak_end = msgs[i]
            cur_len = 1
    if cur_len > max_len:
        max_start, max_end = streak_start, streak_end
    lines.append(
        f"- **最长连续聊天**：{max_len} 条，从 {max_start.timestamp.strftime('%Y-%m-%d %H:%M')} "
        f"到 {max_end.timestamp.strftime('%Y-%m-%d %H:%M')}"
    )

    # 深夜聊天
    late_night = [m for m in msgs if m.timestamp.hour >= 22 or m.timestamp.hour <= 3]
    if late_night:
        sample = late_night[0]
        lines.append(
            f"- **深夜聊天**：共 {len(late_night)} 条，例如 {sample.timestamp.strftime('%Y-%m-%d %H:%M')} "
            f"[{sample.sender}] {sample.content[:40]}"
        )

    # 反复出现的话题
    topic_counter = Counter()
    stopwords = set("的 了 是 我 你 在 和 就 不 人 有 都 个 上 也 很 到 说 要 去 可以 这个 会 好 吗 吧 呢 啊".split())
    word_pattern = re.compile(r"[\u4e00-\u9fa5]{2,4}")
    for m in msgs:
        for w in word_pattern.findall(m.content):
            if w not in stopwords:
                topic_counter[w] += 1
    top_topics = topic_counter.most_common(5)
    if top_topics:
        lines.append(f"- **反复出现的话题**：{', '.join(f'{w}({c})' for w, c in top_topics)}")

    # 重要承诺
    promise_keywords = ["答应", "一定", "永远", "我会", "我承诺", "保证"]
    promises = [m for m in msgs if any(k in m.content for k in promise_keywords)]
    if promises:
        lines.append(f"- **重要承诺**：{len(promises)} 条，例如 [{promises[0].sender}] {promises[0].content[:50]}")

    # 约定事项
    appointment_keywords = ["明天见", "见面", "约会", "一起吃", "去哪儿", "几点", "到时候"]
    appointments = [m for m in msgs if any(k in m.content for k in appointment_keywords)]
    if appointments:
        lines.append(
            f"- **约定事项**：{len(appointments)} 条，例如 [{appointments[0].sender}] {appointments[0].content[:50]}"
        )

    # 争吵/和好
    conflict_keywords = ["吵", "生气", "讨厌", "烦你", "别理我"]
    reconcile_keywords = ["对不起", "抱歉", "原谅", "别生气", "我错了"]
    conflicts = [m for m in msgs if any(k in m.content for k in conflict_keywords)]
    reconciles = [m for m in msgs if any(k in m.content for k in reconcile_keywords)]
    if conflicts:
        lines.append(f"- **争吵片段**：{len(conflicts)} 条，例如 [{conflicts[0].sender}] {conflicts[0].content[:50]}")
    if reconciles:
        lines.append(
            f"- **和好片段**：{len(reconciles)} 条，例如 [{reconciles[0].sender}] {reconciles[0].content[:50]}"
        )

    # 搞笑片段
    funny = [m for m in msgs if "哈哈" in m.content or "笑死" in m.content]
    if funny:
        lines.append(f"- **搞笑片段**：{len(funny)} 条，例如 [{funny[0].sender}] {funny[0].content[:50]}")

    # 回忆录标题候选
    title_candidates = _title_candidates(msgs)
    if title_candidates:
        lines.append("- **标题候选**：")
        for t in title_candidates[:5]:
            lines.append(f"  - {t}")

    text = "\n".join(lines)
    if path:
        p = Path(path)
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(text, encoding="utf-8")
    return text


def _title_candidates(msgs: list[Message]) -> list[str]:
    keywords = ["第一次", "记得", "永远", "喜欢", "爱你", "再见", "重逢", "最好的", "我们", "约定"]
    candidates = []
    for m in msgs:
        text = m.content.strip()
        if 8 <= len(text) <= 30 and any(k in text for k in keywords):
            candidates.append(text)
    return candidates
