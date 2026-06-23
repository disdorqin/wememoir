"""Windows WeChat detection tests (cross-platform: mock the home dir)."""

from __future__ import annotations

from pathlib import Path
from unittest import mock

from wememoir.windows_wechat import detect_wechat_installation
from wememoir.windows_wechat.account_finder import find_account, list_accounts
from wememoir.windows_wechat.detector import resolve_wechat_dir


def _make_fake_wechat(base: Path) -> Path:
    wechat = base / "Documents" / "WeChat Files"
    wechat.mkdir(parents=True)
    (wechat / "wxid_abc123").mkdir()
    (wechat / "wxid_abc123" / "FileStorage").mkdir()
    (wechat / "wxid_abc123" / "Msg").mkdir()
    (wechat / "alice_nick").mkdir()
    (wechat / "alice_nick" / "Multi").mkdir()
    (wechat / "_random_file.txt").write_text("ignore me", encoding="utf-8")
    return wechat


def test_resolve_wechat_dir_from_home(tmp_path: Path):
    wechat = _make_fake_wechat(tmp_path)
    # detector.py builds candidates via os.path.expanduser; we patch the
    # helper that constructs each candidate path so the override-friendly
    # candidate list actually points inside tmp_path.
    real_expanduser = __import__("os").path.expanduser
    def fake_expanduser(p):
        if p == "~":
            return str(tmp_path)
        return real_expanduser(p)
    with mock.patch("wememoir.windows_wechat.detector.os.path.expanduser", side_effect=fake_expanduser):
        resolved = resolve_wechat_dir()
    assert resolved == wechat


def test_detect_accounts(tmp_path: Path):
    wechat = _make_fake_wechat(tmp_path)
    accounts = list_accounts(wechat)
    names = {a.name for a in accounts}
    assert "wxid_abc123" in names
    assert "alice_nick" in names
    assert "_random_file.txt" not in names


def test_find_account_by_partial(tmp_path: Path):
    wechat = _make_fake_wechat(tmp_path)
    a = find_account(wechat, "alice")
    assert a is not None
    assert a.name == "alice_nick"


def test_detect_wechat_installation_returns_dict(tmp_path: Path):
    wechat = _make_fake_wechat(tmp_path)
    with mock.patch("wememoir.windows_wechat.detector.os.path.expanduser", return_value=str(tmp_path)):
        info = detect_wechat_installation(wechat_dir=str(wechat))
    assert info["wechat_dir"] == str(wechat)
    assert len(info["accounts"]) == 2
    assert all("path" in a for a in info["accounts"])


def test_detect_uses_override_only(tmp_path: Path):
    bogus = tmp_path / "does_not_exist"
    info = detect_wechat_installation(wechat_dir=str(bogus))
    assert info["wechat_dir"] is None
    assert info["accounts"] == []
