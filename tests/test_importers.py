from __future__ import annotations

import json

from wememoir.importers import import_file


CSV_CONTENT = """timestamp,sender,content
2023-01-01 10:00,Me,你在吗
2023-01-01 10:01,Alice,在的
2023-01-01 10:02,Me,明天有空吗
2023-01-01 10:03,Alice,有啊
"""

JSON_CONTENT = json.dumps(
    {
        "id": "test",
        "name": "Alice Chat",
        "type": "private",
        "participants": ["Me", "Alice"],
        "messages": [
            {"timestamp": "2023-01-01T10:00:00", "sender": "Me", "content": "你好"},
            {"timestamp": "2023-01-01T10:01:00", "sender": "Alice", "content": "你好呀"},
        ],
    },
    ensure_ascii=False,
)

TXT_CONTENT = """2023-01-01 10:00 Me: 你好
2023-01-01 10:01 Alice: 你好呀
2023-01-01 10:02 Me: 明天见
"""


def test_import_csv(tmp_path):
    path = tmp_path / "chat.csv"
    path.write_text(CSV_CONTENT, encoding="utf-8")
    conv = import_file(str(path), source="csv", self_name="Me")
    assert conv.name == "chat"
    assert len(conv.messages) == 4
    assert conv.messages[0].sender == "Me"
    assert conv.messages[0].sender_type == "self"
    assert conv.messages[1].sender_type == "other"


def test_import_json(tmp_path):
    path = tmp_path / "chat.json"
    path.write_text(JSON_CONTENT, encoding="utf-8")
    conv = import_file(str(path), source="json")
    assert conv.name == "Alice Chat"
    assert len(conv.messages) == 2
    assert conv.participants == ["Me", "Alice"]


def test_import_txt(tmp_path):
    path = tmp_path / "chat.txt"
    path.write_text(TXT_CONTENT, encoding="utf-8")
    conv = import_file(str(path), source="txt", self_name="Me")
    assert len(conv.messages) == 3
    assert conv.messages[0].content == "你好"
    assert conv.messages[2].content == "明天见"
