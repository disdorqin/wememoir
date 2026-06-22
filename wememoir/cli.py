from __future__ import annotations

import argparse
import json
from pathlib import Path

from .cleaners import DialogueCleaner
from .exporters import export_conversation, export_messages
from .importers import import_file
from .memoir import MemoirWriter, generate_highlights
from .models import Conversation
from .skills import build_skill


def _load_conversation(path: str) -> Conversation:
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    return Conversation.from_dict(data)


def cmd_import(args: argparse.Namespace) -> None:
    conversation = import_file(args.file, source=args.source, self_name=args.self_name)
    export_conversation(conversation, args.out)
    print(f"Imported {len(conversation.messages)} messages -> {args.out}")


def cmd_clean(args: argparse.Namespace) -> None:
    conversation = _load_conversation(args.file)
    cleaner = DialogueCleaner()
    cleaned = cleaner.clean(conversation.messages)
    export_messages(cleaned, args.out, title=f"{conversation.name} 清洗后对话")
    print(f"Cleaned {len(conversation.messages)} -> {len(cleaned)} messages -> {args.out}")


def cmd_memoir(args: argparse.Namespace) -> None:
    conversation = _load_conversation(args.file)
    writer = MemoirWriter(conversation)
    writer.write(args.out)
    print(f"Memoir written -> {args.out}")


def cmd_highlights(args: argparse.Namespace) -> None:
    conversation = _load_conversation(args.file)
    generate_highlights(conversation.messages, args.out)
    print(f"Highlights written -> {args.out}")


def cmd_skill(args: argparse.Namespace) -> None:
    conversation = _load_conversation(args.file)
    build_skill(conversation, skill_type=args.type, target=args.target, out_path=args.out)
    print(f"Skill written -> {args.out}")


def cmd_web(args: argparse.Namespace) -> None:
    from .web.app import create_app

    app = create_app()
    app.run(host=args.host, port=args.port, debug=False)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="wememoir", description="本地优先的微信聊天记录整理工具")
    sub = parser.add_subparsers(dest="command", required=True)

    p_import = sub.add_parser("import", help="导入聊天记录文件")
    p_import.add_argument("file", help="输入文件路径")
    p_import.add_argument("--source", default="auto", help="输入格式：auto|csv|json|txt|html")
    p_import.add_argument("--self-name", default=None, help="自己的昵称，用于标记 sender_type=self")
    p_import.add_argument("--out", required=True, help="输出 JSON 路径")
    p_import.set_defaults(func=cmd_import)

    p_clean = sub.add_parser("clean", help="清洗对话")
    p_clean.add_argument("file", help="已导入的 JSON 路径")
    p_clean.add_argument("--out", required=True, help="输出 Markdown 路径")
    p_clean.set_defaults(func=cmd_clean)

    p_memoir = sub.add_parser("memoir", help="生成回忆录")
    p_memoir.add_argument("file", help="已导入的 JSON 路径")
    p_memoir.add_argument("--out", required=True, help="输出 Markdown 路径")
    p_memoir.set_defaults(func=cmd_memoir)

    p_highlights = sub.add_parser("highlights", help="生成 highlights")
    p_highlights.add_argument("file", help="已导入的 JSON 路径")
    p_highlights.add_argument("--out", required=True, help="输出 Markdown 路径")
    p_highlights.set_defaults(func=cmd_highlights)

    p_skill = sub.add_parser("skill", help="生成 AI Skill 包")
    p_skill.add_argument("file", help="已导入的 JSON 路径")
    p_skill.add_argument("--type", default="contact", choices=["contact", "self", "memoir"], help="Skill 类型")
    p_skill.add_argument("--target", default="generic", choices=["generic", "claude", "codex", "cursor"], help="输出目标格式")
    p_skill.add_argument("--out", required=True, help="输出文件路径")
    p_skill.set_defaults(func=cmd_skill)

    p_web = sub.add_parser("web", help="启动本地 Web UI")
    p_web.add_argument("--host", default="127.0.0.1", help="监听地址")
    p_web.add_argument("--port", type=int, default=5000, help="监听端口")
    p_web.set_defaults(func=cmd_web)

    return parser


def main(argv: list[str] | None = None) -> None:
    parser = build_parser()
    args = parser.parse_args(argv)
    args.func(args)


if __name__ == "__main__":
    main()
