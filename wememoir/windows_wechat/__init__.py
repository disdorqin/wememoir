"""Windows WeChat detection and export orchestration.

This module is intentionally limited:

* It only DETECTS paths (WeChat Files directory, account directories, FileStorage).
* It does NOT decrypt the WeChat database, does NOT extract keys, does NOT
  bypass any security mechanism. The actual decoding is delegated to
  user-installed external tools (e.g. ``wechat-cli``).
* It never modifies the original WeChat data. Anything it touches is first
  copied into ``.wememoir_workspace/raw_copy/``.

If you need to extract a database, install a tool you trust yourself and
let WeMemoir's wizard call it as a subprocess.
"""

from __future__ import annotations

from .adapter_base import ExportAdapter, ExportResult
from .detector import detect_wechat_installation
from .export_wizard import doctor_report, export_via_wizard

__all__ = [
    "ExportAdapter",
    "ExportResult",
    "detect_wechat_installation",
    "doctor_report",
    "export_via_wizard",
]
