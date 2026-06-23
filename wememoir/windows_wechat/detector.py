"""Locate the WeChat data directory on Windows.

This module only inspects the file system. It does not open, read, copy, or
modify anything inside the WeChat data directory.
"""

from __future__ import annotations

import os
import platform
import shutil
from pathlib import Path
from typing import Dict, List, Optional


def _candidate_dirs() -> List[Path]:
    """Build the candidate list at call time so tests can override ``~``."""
    user_home = Path(os.path.expanduser("~"))
    username = os.environ.get("USERNAME", "")
    return [
        user_home / "Documents" / "WeChat Files",
        Path("C:/Users") / username / "Documents" / "WeChat Files",
        Path("D:/WeChat Files"),
        Path("E:/WeChat Files"),
    ]


def _default_wechat_dir() -> Path:
    return Path(os.path.expanduser("~")) / "Documents" / "WeChat Files"


ACCOUNT_INDICATORS = ("FileStorage", "Msg", "Multi")


def resolve_wechat_dir(override: Optional[str] = None) -> Optional[Path]:
    """Find a WeChat Files directory.

    Order: explicit override -> known defaults -> PATH lookup.
    Returns the first directory that exists, or None.
    """
    if override:
        p = Path(override).expanduser()
        if p.exists():
            return p
        return None

    for cand in _candidate_dirs():
        if cand.exists() and cand.is_dir():
            return cand

    exe = shutil.which("WeChat") or shutil.which("Weixin") or shutil.which("微信")
    if exe:
        return Path(exe).resolve().parent
    return None


def find_account_dirs(wechat_dir: Path) -> List[Path]:
    """Return immediate subdirectories of ``wechat_dir`` that look like accounts.

    An "account" directory contains at least one of: ``FileStorage``, ``Msg``,
    ``Multi``. Plain top-level files are ignored.
    """
    if not wechat_dir.exists() or not wechat_dir.is_dir():
        return []
    accounts: List[Path] = []
    for child in sorted(wechat_dir.iterdir()):
        if not child.is_dir():
            continue
        try:
            for indicator in ACCOUNT_INDICATORS:
                if (child / indicator).exists():
                    accounts.append(child)
                    break
        except OSError:
            continue
    return accounts


def detect_wechat_installation(wechat_dir: Optional[str] = None) -> Dict[str, object]:
    """Return a structured snapshot of the local WeChat installation.

    The result is JSON-serialisable and safe to print to the user.
    """
    resolved = resolve_wechat_dir(wechat_dir)
    accounts: List[Dict[str, object]] = []
    notes: List[str] = []

    if resolved is None:
        notes.append("WeChat Files directory was not found. Use --wechat-dir to override.")
    else:
        for acc in find_account_dirs(resolved):
            accounts.append(
                {
                    "name": acc.name,
                    "path": str(acc),
                    "has_filestorage": (acc / "FileStorage").exists(),
                    "has_msg": (acc / "Msg").exists(),
                    "has_multi": (acc / "Multi").exists(),
                }
            )
        if not accounts:
            notes.append("WeChat Files directory exists but no account subdirectory was found.")

    wechat_cli = shutil.which("wechat-cli") or shutil.which("wechat_cli")
    chatlog = shutil.which("chatlog") or shutil.which("ChatLogStudio")

    return {
        "platform": platform.platform(),
        "is_windows": platform.system().lower() == "windows",
        "wechat_dir": str(resolved) if resolved else None,
        "accounts": accounts,
        "external_tools": {
            "wechat-cli": wechat_cli,
            "chatlog-studio": chatlog,
        },
        "notes": notes,
    }
