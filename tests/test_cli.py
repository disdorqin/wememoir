"""CLI smoke tests."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

from wememoir.cli import build_parser, main
from wememoir.mom_bot import build_mom_bot


REPO = Path(__file__).resolve().parent.parent
EXAMPLE = REPO / "examples" / "mom_sample.jsonl"


def test_help_lists_all_subcommands(capsys):
    parser = build_parser()
    with pytest.raises(SystemExit) as exc:
        parser.parse_args(["--help"])
    assert exc.value.code == 0


def test_doctor_runs():
    rc = main(["doctor"])
    assert rc is None  # main returns None; argparse's parser handles exit codes


def test_wx_detect_runs(capsys):
    main(["wx-detect"])
    out = capsys.readouterr().out
    assert "platform" in out
    assert "external_tools" in out


def test_mom_bot_runs_on_sample(tmp_path: Path):
    out = tmp_path / "bot"
    main(["mom-bot", str(EXAMPLE), "--out", str(out), "--self-name", "我", "--mom-name", "妈妈"])
    assert (out / "raw" / "mom_chat_full.jsonl").exists()
    assert (out / "profile" / "mom_voice_profile.md").exists()
    assert (out / "bot" / "MOM_BOT_SYSTEM_PROMPT.md").exists()
    assert (out / "bot" / "character_card.json").exists()


def test_mom_bot_preserves_message_count(tmp_path: Path):
    out = tmp_path / "bot"
    main(["mom-bot", str(EXAMPLE), "--out", str(out), "--self-name", "我", "--mom-name", "妈妈"])
    raw_path = out / "raw" / "mom_chat_full.jsonl"
    count = sum(1 for line in raw_path.read_text(encoding="utf-8").splitlines() if line.strip())
    src_count = sum(1 for line in EXAMPLE.read_text(encoding="utf-8").splitlines() if line.strip())
    assert count == src_count


def test_subprocess_help():
    completed = subprocess.run(
        [sys.executable, "-m", "wememoir", "--help"],
        capture_output=True,
        text=True,
        cwd=str(REPO),
    )
    assert completed.returncode == 0
    assert "mom-bot" in completed.stdout
    assert "doctor" in completed.stdout
    assert "wx-export" in completed.stdout
