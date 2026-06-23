from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import List

from .models import Conversation, Message


def _load_conversation(path: str) -> Conversation:
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    return Conversation.from_dict(data)


# ---------------------------------------------------------------------------
# Existing pipeline commands
# ---------------------------------------------------------------------------


def cmd_import(args: argparse.Namespace) -> None:
    from .importers import import_file
    from .exporters import export_conversation

    conversation = import_file(args.file, source=args.source, self_name=args.self_name)
    export_conversation(conversation, args.out)
    print(f"Imported {len(conversation.messages)} messages -> {args.out}")


def cmd_clean(args: argparse.Namespace) -> None:
    from .cleaners import DialogueCleaner
    from .exporters import export_messages

    conversation = _load_conversation(args.file)
    cleaner = DialogueCleaner()
    cleaned = cleaner.clean(conversation.messages)
    export_messages(cleaned, args.out, title=f"{conversation.name} cleaned")
    print(f"Cleaned {len(conversation.messages)} -> {len(cleaned)} messages -> {args.out}")


def cmd_memoir(args: argparse.Namespace) -> None:
    from .memoir import MemoirWriter

    conversation = _load_conversation(args.file)
    writer = MemoirWriter(conversation)
    writer.write(args.out)
    print(f"Memoir written -> {args.out}")


def cmd_highlights(args: argparse.Namespace) -> None:
    from .memoir import generate_highlights

    conversation = _load_conversation(args.file)
    generate_highlights(conversation.messages, args.out)
    print(f"Highlights written -> {args.out}")


def cmd_skill(args: argparse.Namespace) -> None:
    from .skills import build_skill

    conversation = _load_conversation(args.file)
    build_skill(conversation, skill_type=args.type, target=args.target, out_path=args.out)
    print(f"Skill written -> {args.out}")


def cmd_web(args: argparse.Namespace) -> None:
    from .web.app import create_app

    app = create_app()
    app.run(host=args.host, port=args.port, debug=False)


# ---------------------------------------------------------------------------
# Doctor + Windows WeChat wizard
# ---------------------------------------------------------------------------


def cmd_doctor(args: argparse.Namespace) -> None:
    from .windows_wechat import doctor_report

    report = doctor_report(wechat_dir=args.wechat_dir)
    print(json.dumps(report, ensure_ascii=False, indent=2))
    print()
    print("Next steps:")
    for line in report.get("next_steps", []):
        print(f"  - {line}")


def cmd_wx_detect(args: argparse.Namespace) -> None:
    from .windows_wechat import detect_wechat_installation

    info = detect_wechat_installation(wechat_dir=args.wechat_dir)
    print(json.dumps(info, ensure_ascii=False, indent=2))


def cmd_wx_export(args: argparse.Namespace) -> None:
    from .windows_wechat import export_via_wizard

    result = export_via_wizard(
        contact=args.contact,
        out_path=args.out,
        wechat_dir=args.wechat_dir,
        adapter=args.adapter,
    )
    print(json.dumps(result, ensure_ascii=False, indent=2))


# ---------------------------------------------------------------------------
# Mom bot
# ---------------------------------------------------------------------------


def cmd_mom_bot(args: argparse.Namespace) -> None:
    from .mom_bot import build_mom_bot

    summary = build_mom_bot(
        raw_path=args.file,
        out_dir=args.out,
        self_name=args.self_name,
        mom_name=args.mom_name,
    )
    print(json.dumps(summary, ensure_ascii=False, indent=2))


def cmd_mom_chat(args: argparse.Namespace) -> None:
    from .mom_bot import run_mom_chat_server

    run_mom_chat_server(bot_dir=args.file, host=args.host, port=args.port)


# ---------------------------------------------------------------------------
# Parser
# ---------------------------------------------------------------------------


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="wememoir",
        description="Local-first WeChat chat organizer, exporter and mom-style comfort bot generator",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    p_import = sub.add_parser("import", help="Import a chat export file")
    p_import.add_argument("file", help="Input file path")
    p_import.add_argument("--source", default="auto", help="auto|csv|json|txt|html|jsonl")
    p_import.add_argument("--self-name", default=None, help="Your nickname to mark sender_type=self")
    p_import.add_argument("--out", required=True, help="Output JSON path")
    p_import.set_defaults(func=cmd_import)

    p_clean = sub.add_parser("clean", help="Clean the dialogue")
    p_clean.add_argument("file", help="Imported JSON path")
    p_clean.add_argument("--out", required=True, help="Output Markdown path")
    p_clean.set_defaults(func=cmd_clean)

    p_memoir = sub.add_parser("memoir", help="Generate memoir")
    p_memoir.add_argument("file", help="Imported JSON path")
    p_memoir.add_argument("--out", required=True, help="Output Markdown path")
    p_memoir.set_defaults(func=cmd_memoir)

    p_highlights = sub.add_parser("highlights", help="Generate highlights")
    p_highlights.add_argument("file", help="Imported JSON path")
    p_highlights.add_argument("--out", required=True, help="Output Markdown path")
    p_highlights.set_defaults(func=cmd_highlights)

    p_skill = sub.add_parser("skill", help="Build an AI skill package")
    p_skill.add_argument("file", help="Imported JSON path")
    p_skill.add_argument("--type", default="contact", choices=["contact", "self", "memoir"])
    p_skill.add_argument("--target", default="generic", choices=["generic", "claude", "codex", "cursor"])
    p_skill.add_argument("--out", required=True, help="Output file path")
    p_skill.set_defaults(func=cmd_skill)

    p_web = sub.add_parser("web", help="Run the generic Web UI")
    p_web.add_argument("--host", default="127.0.0.1")
    p_web.add_argument("--port", type=int, default=5000)
    p_web.set_defaults(func=cmd_web)

    # --- doctor / wx-* / mom-* ---
    p_doctor = sub.add_parser("doctor", help="Inspect the local environment")
    p_doctor.add_argument("--wechat-dir", default=None, help="Override WeChat Files directory")
    p_doctor.set_defaults(func=cmd_doctor)

    p_wxd = sub.add_parser("wx-detect", help="Detect Windows WeChat data directory and accounts")
    p_wxd.add_argument("--wechat-dir", default=None, help="Override WeChat Files directory")
    p_wxd.set_defaults(func=cmd_wx_detect)

    p_wxe = sub.add_parser("wx-export", help="Export chat history (raw preservation) for a contact")
    p_wxe.add_argument("--contact", required=True, help="Contact name or wxid")
    p_wxe.add_argument("--out", required=True, help="Output JSONL path (raw, never filtered)")
    p_wxe.add_argument("--wechat-dir", default=None, help="Override WeChat Files directory")
    p_wxe.add_argument(
        "--adapter",
        default="auto",
        choices=["auto", "wechat-cli", "chatlog-studio", "manual"],
        help="Which external exporter to use (auto = first available)",
    )
    p_wxe.set_defaults(func=cmd_wx_export)

    p_mom = sub.add_parser("mom-bot", help="Build a mom-style comfort bot data package")
    p_mom.add_argument("file", help="Raw JSONL path (mom_raw.jsonl)")
    p_mom.add_argument("--out", required=True, help="Output directory")
    p_mom.add_argument("--self-name", default="我", help="Your nickname")
    p_mom.add_argument("--mom-name", default="妈妈", help="Mom's nickname")
    p_mom.set_defaults(func=cmd_mom_bot)

    p_mc = sub.add_parser("mom-chat", help="Run the local mom-style chat UI")
    p_mc.add_argument("file", help="Path to the mom-bot output directory")
    p_mc.add_argument("--host", default="127.0.0.1")
    p_mc.add_argument("--port", type=int, default=5050)
    p_mc.set_defaults(func=cmd_mom_chat)

    return parser


def main(argv: List[str] | None = None) -> None:
    parser = build_parser()
    args = parser.parse_args(argv)
    args.func(args)


if __name__ == "__main__":
    main()
