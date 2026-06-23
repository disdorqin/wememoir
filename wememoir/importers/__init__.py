from __future__ import annotations

from pathlib import Path
from typing import Dict, Callable

from .csv_importer import import_csv
from .json_importer import import_json
from .jsonl_importer import import_jsonl
from .txt_importer import import_txt
from .html_importer import import_html


IMPORTERS: Dict[str, Callable] = {
    "csv": import_csv,
    "json": import_json,
    "jsonl": import_jsonl,
    "txt": import_txt,
    "html": import_html,
}


def import_file(path: str, source: str = "auto", self_name: str | None = None):
    p = Path(path)
    if source == "auto":
        source = p.suffix.lower().lstrip(".")
        if source not in IMPORTERS:
            with open(p, encoding="utf-8-sig") as f:
                sample = f.read(512).strip()
            first_line = sample.splitlines()[0] if sample else ""
            if sample.startswith(("[", "{")):
                source = "json"
            elif "," in first_line and first_line.count(",") >= 2:
                source = "csv"
            else:
                source = "txt"

    if source not in IMPORTERS:
        raise ValueError(f"Unsupported source: {source}")

    conversation = IMPORTERS[source](path)

    if self_name:
        for m in conversation.messages:
            if m.sender == self_name:
                m.sender_type = "self"

    return conversation
