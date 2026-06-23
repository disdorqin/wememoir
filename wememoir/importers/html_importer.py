from __future__ import annotations

from pathlib import Path

try:
    from bs4 import BeautifulSoup
except Exception:  # pragma: no cover
    BeautifulSoup = None  # type: ignore

from ..models import Conversation
from .txt_importer import parse_text


def import_html(path: str) -> Conversation:
    p = Path(path)
    html = p.read_text(encoding="utf-8-sig")

    if BeautifulSoup is not None:
        soup = BeautifulSoup(html, "html.parser")
        # Remove script/style to avoid noise
        for tag in soup(["script", "style"]):
            tag.decompose()
        text = soup.get_text("\n")
    else:
        # Fallback: crude tag stripping
        import re
        text = re.sub(r"<[^>]+>", "\n", html)

    conversation = parse_text(text)
    conversation.name = p.stem
    return conversation
