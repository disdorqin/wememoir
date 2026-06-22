from __future__ import annotations

from datetime import datetime, timedelta

from wememoir.cleaners import DialogueCleaner, is_filler
from wememoir.models import Message


def _msg(content: str, sender: str = "Me", delta_min: int = 0) -> Message:
    return Message(
        id="x",
        timestamp=datetime(2023, 1, 1, 10, 0, 0) + timedelta(minutes=delta_min),
        sender=sender,
        content=content,
        raw_content=content,
    )


def test_is_filler_true():
    assert is_filler("嗯")
    assert is_filler("哈哈")
    assert is_filler("哈哈哈哈")
    assert is_filler("666")
    assert is_filler("嗯嗯")


def test_is_filler_false():
    assert not is_filler("哈哈，真的吗")
    assert not is_filler("你在吗")
    assert not is_filler("今天天气不错")


def test_remove_filler():
    cleaner = DialogueCleaner()
    messages = [
        _msg("你在吗", "Alice"),
        _msg("嗯", "Me"),
        _msg("明天见", "Me"),
    ]
    cleaned = cleaner.clean(messages)
    assert len(cleaned) == 2
    assert all("嗯" not in m.content for m in cleaned)


def test_keep_meaningful_short():
    cleaner = DialogueCleaner()
    messages = [_msg("好", "Alice"), _msg("我在", "Me"), _msg("明天见", "Alice")]
    cleaned = cleaner.clean(messages)
    assert len(cleaned) == 3


def test_merge_consecutive_short():
    cleaner = DialogueCleaner()
    messages = [
        _msg("你在吗", "Me", 0),
        _msg("明天有空吗", "Me", 1),
        _msg("有啊", "Alice", 2),
    ]
    cleaned = cleaner.clean(messages)
    assert len(cleaned) == 2
    assert "你在吗" in cleaned[0].content
    assert "明天有空吗" in cleaned[0].content
    assert cleaned[1].content == "有啊"


def test_remove_system_and_placeholders():
    cleaner = DialogueCleaner()
    messages = [
        _msg("[图片]", "Alice"),
        _msg("你撤回了一条消息", "Me"),
        _msg("你好", "Alice"),
    ]
    cleaned = cleaner.clean(messages)
    assert len(cleaned) == 1
    assert cleaned[0].content == "你好"
