"""Adapter for the optional ``wechat-cli`` external exporter.

This adapter only RUNS an external ``wechat-cli`` binary that the user has
installed themselves. It does not bundle any decryption logic.

If ``wechat-cli`` is not installed, the adapter reports a clean
``ExportResult(ok=False, ...)`` with a human-readable install hint.
"""

from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path
from typing import List, Optional

from .adapter_base import ExportAdapter, ExportResult


class WeChatCliAdapter(ExportAdapter):
    name = "wechat-cli"
    install_hint = (
        "Install wechat-cli yourself (e.g. `pipx install wechat-cli` or from its official "
        "release), authorise it against your own desktop WeChat, and re-run this command. "
        "WeMemoir never bundles, distributes or invokes any decryption code itself."
    )
    binary_names = ("wechat-cli", "wechat_cli")

    def run_export(
        self,
        contact: str,
        out_path: Path,
        wechat_dir: Optional[Path] = None,
    ) -> ExportResult:
        binary = shutil.which(self.binary_names[0]) or shutil.which(self.binary_names[1])
        if not binary:
            return ExportResult(
                ok=False,
                adapter=self.name,
                out_path=None,
                raw_messages=0,
                note=f"wechat-cli not found on PATH. {self.install_hint}",
            )

        out_path.parent.mkdir(parents=True, exist_ok=True)

        cmd: List[str] = [binary, "export", "--contact", contact, "--format", "jsonl"]
        if wechat_dir is not None:
            cmd.extend(["--wechat-dir", str(wechat_dir)])
        cmd.extend(["--out", str(out_path)])

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
                note=f"failed to spawn wechat-cli: {exc}",
            )
        except subprocess.TimeoutExpired:
            return ExportResult(
                ok=False,
                adapter=self.name,
                out_path=None,
                raw_messages=0,
                note="wechat-cli timed out after 300s",
            )

        if completed.returncode != 0:
            return ExportResult(
                ok=False,
                adapter=self.name,
                out_path=None,
                raw_messages=0,
                note=(completed.stderr or completed.stdout or "").strip() or "wechat-cli failed",
            )

        if not out_path.exists():
            return ExportResult(
                ok=False,
                adapter=self.name,
                out_path=out_path,
                raw_messages=0,
                note="wechat-cli exited 0 but did not produce the output file",
            )

        try:
            count = sum(1 for _ in out_path.open("r", encoding="utf-8") if _.strip())
        except OSError as exc:
            return ExportResult(
                ok=False,
                adapter=self.name,
                out_path=out_path,
                raw_messages=0,
                note=f"cannot read exported file: {exc}",
            )

        return ExportResult(
            ok=True,
            adapter=self.name,
            out_path=out_path,
            raw_messages=count,
            note="exported via wechat-cli",
        )
