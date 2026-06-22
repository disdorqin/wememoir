from __future__ import annotations

import json
import os
import shutil
import tempfile
import uuid
import zipfile
from pathlib import Path

from flask import Flask, redirect, render_template, request, send_file, url_for

from ..cleaners import DialogueCleaner
from ..exporters import export_conversation, export_messages
from ..importers import import_file
from ..memoir import MemoirWriter, generate_highlights
from ..models import Conversation
from ..skills import build_skill


def create_app() -> Flask:
    app = Flask(__name__, template_folder="templates", static_folder="static")
    app.config["MAX_CONTENT_LENGTH"] = 128 * 1024 * 1024

    work_root = Path(tempfile.gettempdir()) / "wememoir_web"
    work_root.mkdir(exist_ok=True)

    def _job_dir(job_id: str) -> Path:
        d = work_root / job_id
        d.mkdir(exist_ok=True)
        return d

    def _load(job_id: str) -> Conversation:
        path = _job_dir(job_id) / "imported.json"
        data = json.loads(path.read_text(encoding="utf-8"))
        return Conversation.from_dict(data)

    @app.route("/")
    def index():
        return render_template("index.html")

    @app.route("/import", methods=["POST"])
    def do_import():
        uploaded = request.files.get("file")
        if not uploaded or not uploaded.filename:
            return "未选择文件", 400
        source = request.form.get("source", "auto")
        self_name = request.form.get("self_name") or None
        job_id = uuid.uuid4().hex
        d = _job_dir(job_id)
        src_path = d / uploaded.filename
        uploaded.save(str(src_path))

        conversation = import_file(str(src_path), source=source, self_name=self_name)
        export_conversation(conversation, str(d / "imported.json"))
        return redirect(url_for("workbench", job_id=job_id))

    @app.route("/work/<job_id>")
    def workbench(job_id: str):
        conversation = _load(job_id)
        return render_template(
            "workbench.html",
            job_id=job_id,
            name=conversation.name,
            participants=conversation.participants,
            message_count=len(conversation.messages),
            messages=conversation.messages[:100],
        )

    @app.route("/work/<job_id>/clean")
    def do_clean(job_id: str):
        conversation = _load(job_id)
        cleaner = DialogueCleaner()
        cleaned = cleaner.clean(conversation.messages)
        export_messages(cleaned, str(_job_dir(job_id) / "cleaned.md"), title=f"{conversation.name} 清洗后对话")
        return redirect(url_for("download", job_id=job_id, filename="cleaned.md"))

    @app.route("/work/<job_id>/memoir")
    def do_memoir(job_id: str):
        conversation = _load(job_id)
        writer = MemoirWriter(conversation)
        writer.write(str(_job_dir(job_id) / "memoir.md"))
        return redirect(url_for("download", job_id=job_id, filename="memoir.md"))

    @app.route("/work/<job_id>/highlights")
    def do_highlights(job_id: str):
        conversation = _load(job_id)
        generate_highlights(conversation.messages, str(_job_dir(job_id) / "highlights.md"))
        return redirect(url_for("download", job_id=job_id, filename="highlights.md"))

    @app.route("/work/<job_id>/skill")
    def do_skill(job_id: str):
        conversation = _load(job_id)
        skill_type = request.args.get("type", "contact")
        target = request.args.get("target", "generic")
        filename = "AGENTS.md" if target == "codex" else ("cursor_rule.mdc" if target == "cursor" else "SKILL.md")
        build_skill(conversation, skill_type=skill_type, target=target, out_path=str(_job_dir(job_id) / filename))
        return redirect(url_for("download", job_id=job_id, filename=filename))

    @app.route("/work/<job_id>/zip")
    def do_zip(job_id: str):
        d = _job_dir(job_id)
        zip_path = d / "wememoir_export.zip"
        with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
            for name in ["imported.json", "cleaned.md", "memoir.md", "highlights.md", "SKILL.md", "AGENTS.md", "cursor_rule.mdc"]:
                p = d / name
                if p.exists():
                    zf.write(p, arcname=name)
        return redirect(url_for("download", job_id=job_id, filename="wememoir_export.zip"))

    @app.route("/download/<job_id>/<filename>")
    def download(job_id: str, filename: str):
        p = _job_dir(job_id) / filename
        if not p.exists():
            return "文件不存在", 404
        return send_file(str(p), as_attachment=True, download_name=filename)

    return app
