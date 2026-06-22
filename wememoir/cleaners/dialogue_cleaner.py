from __future__ import annotations

from ..models import Message
from .dedupe import deduplicate
from .filler_rules import is_filler


class DialogueCleaner:
    """Turn raw messages into a normal readable dialogue."""

    _RECALL_KEYWORDS = ["撤回了一条消息", "消息已撤回", "你撤回了一条消息"]
    _PLACEHOLDERS = {"[图片]", "[语音]", "[视频]", "[动画表情]", "[表情包]", "[文件]", "[位置]", "[链接]"}

    def __init__(self, merge_window_sec: int = 300, merge_max_len: int = 40):
        self.merge_window_sec = merge_window_sec
        self.merge_max_len = merge_max_len

    def clean(self, messages: list[Message]) -> list[Message]:
        messages = sorted(messages, key=lambda m: m.timestamp)
        filtered: list[Message] = []
        for m in messages:
            if not m.content.strip():
                continue
            if m.message_type == "system":
                continue
            if self._is_recall(m.content):
                continue
            if self._is_placeholder(m.content):
                continue
            if is_filler(m.content):
                continue
            filtered.append(m)

        filtered = deduplicate(filtered)
        return self._merge_consecutive(filtered)

    def _is_recall(self, content: str) -> bool:
        return any(kw in content for kw in self._RECALL_KEYWORDS)

    def _is_placeholder(self, content: str) -> bool:
        return content.strip() in self._PLACEHOLDERS

    def _merge_consecutive(self, messages: list[Message]) -> list[Message]:
        if not messages:
            return []
        merged: list[Message] = [messages[0]]
        for m in messages[1:]:
            prev = merged[-1]
            same_sender = m.sender == prev.sender
            close = (m.timestamp - prev.timestamp).total_seconds() <= self.merge_window_sec
            short = len(prev.content) <= self.merge_max_len and len(m.content) <= self.merge_max_len
            text_types = prev.message_type == "text" and m.message_type == "text"

            if same_sender and close and short and text_types:
                prev.content = self._join(prev.content, m.content)
                prev.raw_content = prev.raw_content + "\n" + m.raw_content
            else:
                merged.append(m)
        return merged

    def _join(self, left: str, right: str) -> str:
        left_stripped = left.rstrip()
        if not left_stripped:
            return right
        last_char = left_stripped[-1]
        if last_char in "。？?！!；;":
            return left_stripped + " " + right
        if last_char in "吗呢吧":
            return left_stripped + "？" + right
        return left_stripped + "，" + right
