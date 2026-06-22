from __future__ import annotations

from pathlib import Path

from ..models import Message


def export_messages(messages: list[Message], path: str, title: str = "对话") -> None:
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)

    lines: list[str] = [f"# {title}", ""]
    current_date = ""
    for m in messages:
        date_label = m.timestamp.strftime("%Y-%m-%d")
        if date_label != current_date:
            lines.append(f"## {date_label}")
            lines.append("")
            current_date = date_label
        lines.append(f"[{m.sender}] {m.content}")
        lines.append("")

    p.write_text("\n".join(lines), encoding="utf-8")
