"""Adapter base class for external WeChat exporters.

An adapter wraps a third-party tool that the user has installed themselves
(e.g. ``wechat-cli``). The adapter's job is to:

* describe the tool and how to install it,
* invoke the tool as a subprocess,
* read its JSON / JSONL output,
* and write the resulting raw messages to ``.wememoir_workspace/raw_copy/``.

Adapters MUST NOT touch the WeChat data directory itself. The third-party
tool is responsible for that. WeMemoir just reads what the tool produced.
"""

from __future__ import annotations

import shutil
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional


@dataclass
class ExportResult:
    ok: bool
    adapter: str
    out_path: Optional[Path]
    raw_messages: int
    note: str = ""

    def to_dict(self) -> dict:
        return {
            "ok": self.ok,
            "adapter": self.adapter,
            "out_path": str(self.out_path) if self.out_path else None,
            "raw_messages": self.raw_messages,
            "note": self.note,
        }


class ExportAdapter:
    """Base class for external exporter adapters."""

    name: str = "base"
    install_hint: str = ""
    binary_names: tuple = ()

    def is_available(self) -> bool:
        for bin_name in self.binary_names:
            if shutil.which(bin_name):
                return True
        return False

    def describe(self) -> dict:
        return {
            "name": self.name,
            "available": self.is_available(),
            "binary": list(self.binary_names),
            "install_hint": self.install_hint,
        }

    def run_export(
        self,
        contact: str,
        out_path: Path,
        wechat_dir: Optional[Path] = None,
    ) -> ExportResult:
        raise NotImplementedError

    @staticmethod
    def available_adapters(adapters: List["ExportAdapter"]) -> List["ExportAdapter"]:
        return [a for a in adapters if a.is_available()]
