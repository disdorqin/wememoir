from __future__ import annotations

from pathlib import Path
from typing import List

from ..models import Conversation, Message
from .chapter_builder import build_chapters, stage_name
from .timeline import build_timeline


class MemoirWriter:
    """生成章节式聊天回忆录。"""

    def __init__(self, conversation: Conversation):
        self.conversation = conversation

    def write(self, path: str | None = None) -> str:
        msgs = build_timeline(self.conversation.messages)
        chapters = build_chapters(msgs)

        lines: List[str] = []
        lines.append(f"# {self.conversation.name} 聊天回忆录")
        lines.append("")

        if msgs:
            start = msgs[0].timestamp.strftime("%Y-%m-%d")
            end = msgs[-1].timestamp.strftime("%Y-%m-%d")
            lines.append(f"**时间范围**：{start} ~ {end}")
        lines.append(f"**消息总数**：{len(msgs)}")
        lines.append(f"**参与人**：{', '.join(self.conversation.participants)}")
        lines.append("")

        for idx, chapter in enumerate(chapters):
            stage = stage_name(idx, chapter, len(chapters))
            cstart = chapter[0].timestamp.strftime("%Y-%m-%d")
            cend = chapter[-1].timestamp.strftime("%Y-%m-%d")

            lines.append(f"## {stage}（{cstart} ~ {cend}）")
            lines.append("")
            lines.append(f"**主要事件**：本阶段共有 {len(chapter)} 条消息。")

            quotes = self._pick_quotes(chapter)
            if quotes:
                lines.append("")
                lines.append("**代表性原话**：")
                for q in quotes:
                    lines.append(f"> [{q.sender}] {q.content}")

            lines.append("")
            lines.append(f"**情绪变化**：{self._emotion_summary(chapter)}")

            lines.append("")
            lines.append(
                f"**重要时间点**：{chapter[0].timestamp.strftime('%Y-%m-%d %H:%M')} 开始，"
                f"{chapter[-1].timestamp.strftime('%Y-%m-%d %H:%M')} 结束。"
            )
            lines.append("")

            # 值得保留的片段：取本阶段前 5 条可读对话
            lines.append("**值得保留的片段**：")
            for m in chapter[:5]:
                lines.append(f"- [{m.sender}] {m.content}")
            lines.append("")

        text = "\n".join(lines)
        if path:
            p = Path(path)
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(text, encoding="utf-8")
        return text

    def _pick_quotes(self, chapter: list[Message]) -> list[Message]:
        if not chapter:
            return []
        candidates = [chapter[0]]
        longest = max(chapter, key=lambda m: len(m.content))
        if longest not in candidates:
            candidates.append(longest)
        # 优先选择包含情绪词或关键信息的句子
        keywords = ["喜欢", "爱", "对不起", "抱歉", "永远", "记得", "约定", "明天", "见面", "分手", "再见", "答应"]
        for m in chapter:
            if any(kw in m.content for kw in keywords) and m not in candidates:
                candidates.append(m)
                if len(candidates) >= 5:
                    break
        return candidates[:5]

    def _emotion_summary(self, chapter: list[Message]) -> str:
        positive = sum(1 for m in chapter if any(k in m.content for k in ["哈哈", "开心", "喜欢", "爱", "棒", "好"]))
        negative = sum(1 for m in chapter if any(k in m.content for k in ["难过", "伤心", "生气", "烦", "恨", "哭"]))
        neutral = len(chapter) - positive - negative
        parts = []
        if positive:
            parts.append(f"愉悦 {positive} 次")
        if negative:
            parts.append(f"低落/争执 {negative} 次")
        if neutral:
            parts.append(f"平静 {neutral} 次")
        if not parts:
            return "情绪平稳"
        return "、".join(parts) + "。"
