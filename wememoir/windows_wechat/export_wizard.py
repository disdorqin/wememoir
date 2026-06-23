"""Top-level export wizard.

The wizard coordinates the user-installed external exporter and the local
``raw_copy/`` workspace. It does not extract anything by itself.
"""

from __future__ import annotations

import json
import shutil
from pathlib import Path
from typing import Dict, List, Optional

from .account_finder import find_account, list_accounts
from .adapter_base import ExportAdapter, ExportResult
from .chatlog_studio_adapter import ChatlogStudioAdapter
from .detector import detect_wechat_installation, resolve_wechat_dir
from .wechat_cli_adapter import WeChatCliAdapter


WORKSPACE_DIR = Path(".wememoir_workspace")
RAW_COPY_DIR = WORKSPACE_DIR / "raw_copy"


def _copy_to_workspace(src: Path) -> Path:
    """Copy an exported file into ``.wememoir_workspace/raw_copy/`` for safety.

    We never modify the original. This is the only filesystem side effect
    the wizard performs.
    """
    RAW_COPY_DIR.mkdir(parents=True, exist_ok=True)
    target = RAW_COPY_DIR / src.name
    shutil.copy2(src, target)
    return target


def _build_adapter_chain() -> List[ExportAdapter]:
    return [WeChatCliAdapter(), ChatlogStudioAdapter()]


def doctor_report(wechat_dir: Optional[str] = None) -> Dict[str, object]:
    info = detect_wechat_installation(wechat_dir=wechat_dir)
    info["adapters"] = [a.describe() for a in _build_adapter_chain()]
    next_steps: List[str] = []
    if not info.get("wechat_dir"):
        next_steps.append(
            "Set --wechat-dir to point at your WeChat Files directory, or log into WeChat "
            "on Windows at least once so that the default Documents\\WeChat Files directory exists."
        )
    elif not info.get("accounts"):
        next_steps.append("Log into WeChat on Windows so an account directory is created.")
    if not any(a.get("available") for a in info["adapters"]):
        next_steps.append(
            "No external WeChat exporter is installed. Either install `wechat-cli` or "
            "`ChatLog Studio` yourself, or pre-export your chat history as CSV/JSON/JSONL "
            "and use `wememoir import <file>` directly."
        )
    next_steps.append(
        "Always copy the original WeChat data is not modified. Pre-exported files should "
        "be placed in .wememoir_workspace/raw_copy/ before processing."
    )
    info["next_steps"] = next_steps
    return info


def export_via_wizard(
    contact: str,
    out_path: str,
    wechat_dir: Optional[str] = None,
    adapter: str = "auto",
) -> Dict[str, object]:
    """Run the export wizard and write the raw JSONL output to ``out_path``.

    Returns a JSON-serialisable status dict.
    """
    out = Path(out_path)
    out.parent.mkdir(parents=True, exist_ok=True)

    resolved = resolve_wechat_dir(wechat_dir)

    notes: List[str] = []
    candidates: List[Dict[str, str]] = []
    if resolved is not None:
        for acc in list_accounts(resolved):
            candidates.append({"name": acc.name, "path": str(acc.path)})

    chain = _build_adapter_chain()
    if adapter != "auto":
        chain = [a for a in chain if a.name == adapter]
        if not chain:
            return {
                "ok": False,
                "stage": "adapter-selection",
                "error": f"unknown adapter: {adapter}",
            }

    available = [a for a in chain if a.is_available()]
    if not available:
        return {
            "ok": False,
            "stage": "adapter-selection",
            "error": "no external WeChat exporter is installed and accessible",
            "hint": "install wechat-cli or ChatLog Studio yourself, then re-run",
            "candidates": candidates,
        }

    last: Optional[ExportResult] = None
    for a in available:
        result = a.run_export(contact=contact, out_path=out, wechat_dir=resolved)
        last = result
        if result.ok:
            safe_copy = _copy_to_workspace(out)
            return {
                "ok": True,
                "stage": "exported",
                "adapter": result.adapter,
                "raw_messages": result.raw_messages,
                "out_path": str(out),
                "raw_copy": str(safe_copy),
                "candidates": candidates,
                "note": result.note,
            }
        notes.append(f"{a.name}: {result.note}")

    return {
        "ok": False,
        "stage": "export",
        "error": "all available adapters failed",
        "notes": notes,
        "candidates": candidates,
    }
