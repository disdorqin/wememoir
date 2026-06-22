from __future__ import annotations

import json
from pathlib import Path

from ..models import Conversation


def export_conversation(conversation: Conversation, path: str) -> None:
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(conversation.to_dict(), ensure_ascii=False, indent=2), encoding="utf-8")
