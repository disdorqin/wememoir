"""Account directory helpers.

Account directories under ``WeChat Files/`` look like ``wxid_xxxxxxxx`` or
a user nickname. This module only inspects their structure; it never opens
the underlying ``.db`` files.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional


@dataclass
class AccountInfo:
    name: str
    path: Path
    has_filestorage: bool
    has_msg: bool
    has_multi: bool

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "path": str(self.path),
            "has_filestorage": self.has_filestorage,
            "has_msg": self.has_msg,
            "has_multi": self.has_multi,
        }


def list_accounts(wechat_dir: Path) -> List[AccountInfo]:
    """Return all account directories under ``wechat_dir``."""
    if not wechat_dir.exists() or not wechat_dir.is_dir():
        return []
    accounts: List[AccountInfo] = []
    for child in sorted(wechat_dir.iterdir()):
        if not child.is_dir():
            continue
        has_fs = (child / "FileStorage").exists()
        has_msg = (child / "Msg").exists()
        has_multi = (child / "Multi").exists()
        if has_fs or has_msg or has_multi:
            accounts.append(
                AccountInfo(
                    name=child.name,
                    path=child,
                    has_filestorage=has_fs,
                    has_msg=has_msg,
                    has_multi=has_multi,
                )
            )
    return accounts


def find_account(wechat_dir: Path, contact: str) -> Optional[AccountInfo]:
    """Find an account whose name matches ``contact``.

    The match is case-insensitive and accepts partial names. Returns None
    if multiple candidates match and the input is ambiguous.
    """
    accounts = list_accounts(wechat_dir)
    if not accounts:
        return None

    needle = contact.strip().lower()
    if not needle:
        return None

    exact = [a for a in accounts if a.name.lower() == needle]
    if len(exact) == 1:
        return exact[0]
    if len(exact) > 1:
        return exact[0]  # deterministic tie-break

    partial = [a for a in accounts if needle in a.name.lower()]
    if len(partial) == 1:
        return partial[0]
    return None
