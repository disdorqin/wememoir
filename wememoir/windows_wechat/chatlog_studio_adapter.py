"""Adapter for the optional ``ChatLog Studio`` external exporter.

This is a stub that documents how a real adapter should look. It only runs
an external binary if it is present; otherwise it returns a clean error.
"""

from __future__ import annotations

import shutil
import subprocess
from pathlib import Path
from typing import List, Optional

from .adapter_base import ExportAdapter, ExportResult


class ChatlogStudioAdapter(ExportAdapter):
    name = "chatlog-studio"
    install_hint = (
        "Install ChatLog Studio yourself from its official site, point it at your own "
        "WeChat data, and re-run this command. WeMemoir never bundles ChatLog Studio."
    )
    binary_names = ("chatlog", "ChatLogStudio", "chatlog-studio")

    def run_export(
        self,
        contact: str,
        out_path: Path,
        wechat_dir: Optional[Path] = None,
    ) -> ExportResult:
        binary = None
        for n in self.binary_names:
            binary = shutil.which(n)
            if binary:
                break
        if not binary:
            return ExportResult(
                ok=False,
                adapter=self.name,
                out_path=None,
                raw_messages=0,
                note=f"chatlog-studio not found on PATH. {self.install_hint}",
            )

        out_path.parent.mkdir(parents=True, exist_ok=True)

        cmd: List[str] = [binary, "export", "--contact", contact, "--out", str(out_path)]
        if wechat_dir is not None:
            cmd.extend(["--source", str(wechat_dir)])

        try:
            completed = subprocess.run(
                cmd,
                check=False,
                capture_output=True,
                text=True,
                timeout=300,
            )
        except FileNotFoundError as exc:
            return ExportResult(
                ok=False,
                adapter=self.name,
                out_path=None,
                raw_messages=0,
                note=f"failed to spawn chatlog-studio: {exc}",
            )
        except subprocess.TimeoutExpired:
            return ExportResult(
                ok=False,
                adapter=self.name,
                out_path=None,
                raw_messages=0,
                note="chatlog-studio timed out after 300s",
            )

        if completed.returncode != 0 or not out_path.exists():
            return ExportResult(
                ok=False,
                adapter=self.name,
                out_path=out_path if out_path.exists() else None,
                raw_messages=0,
                note=(completed.stderr or completed.stdout or "").strip() or "chatlog-studio failed",
            )

        count = sum(1 for line in out_path.open("r", encoding="utf-8") if line.strip())
        return ExportResult(
            ok=True,
            adapter=self.name,
            out_path=out_path,
            raw_messages=count,
            note="exported via chatlog-studio",
        )
