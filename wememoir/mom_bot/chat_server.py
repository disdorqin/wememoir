"""Local chat UI for the mom-style bot.

Runs a small Flask app on 127.0.0.1. Loads the generated system prompt
plus a small raw excerpt and forwards the user's message to a configured
LLM API (OpenAI-compatible). The API key is read from ``.env`` and is
NEVER written into the source code or stored on disk by this module.

If no API key is configured, the UI still works in "demo" mode: it shows
the system prompt and the raw excerpt, but does not call any LLM.
"""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import List, Optional

try:
    from flask import Flask, jsonify, render_template_string, request
except Exception:  # pragma: no cover - flask is a runtime dep
    Flask = None  # type: ignore


INDEX_HTML = """\
<!doctype html>
<html lang="zh">
<head>
<meta charset="utf-8" />
<title>妈妈风格陪伴 Bot</title>
<style>
  body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
         max-width: 900px; margin: 20px auto; padding: 0 12px; color: #222; }
  h1 { font-size: 20px; }
  .meta { color: #777; font-size: 12px; }
  .chat { border: 1px solid #ddd; border-radius: 8px; padding: 12px;
          min-height: 320px; background: #fafafa; }
  .msg { margin: 6px 0; }
  .me { text-align: right; color: #06c; }
  .mom { text-align: left; color: #333; }
  textarea { width: 100%; height: 70px; margin-top: 8px; }
  button { padding: 6px 12px; }
  pre { white-space: pre-wrap; background: #f4f4f4; padding: 8px;
        border-radius: 6px; max-height: 240px; overflow: auto; }
  .warning { background: #fff7e6; border: 1px solid #f5c97a; padding: 8px;
             border-radius: 6px; }
</style>
</head>
<body>
  <h1>妈妈风格陪伴 Bot</h1>
  <div class="meta">仅本地运行 · 不会自动发微信消息 · 不会上传你的聊天记录</div>

  <div class="warning">
    <strong>使用前必读</strong>：本 Bot 不是你的亲生母亲；它不会假装在现实里陪着你；
    不会编造记录里没有的事实；如果你情绪崩溃 / 想不开，请联系现实中的亲人朋友
    或 24 小时心理援助热线。
  </div>

  <p>LLM 状态：<b>{{ llm_status }}</b></p>

  <div class="chat" id="chat">
    {% for m in history %}
      <div class="msg {{ m.role }}"><b>{{ m.who }}：</b>{{ m.text }}</div>
    {% endfor %}
  </div>

  <textarea id="input" placeholder="和妈妈说点什么..."></textarea>
  <button onclick="send()">发送</button>
  <button onclick="clearChat()">清空</button>

  <h3>系统提示词（只读）</h3>
  <pre>{{ system_prompt_excerpt }}</pre>

<script>
  async function send() {
    const text = document.getElementById('input').value.trim();
    if (!text) return;
    append('me', '我', text);
    document.getElementById('input').value = '';
    const res = await fetch('/api/chat', { method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ message: text }) });
    const data = await res.json();
    append('mom', '妈', data.reply || '(没有回复)');
  }
  function clearChat() { document.getElementById('chat').innerHTML = ''; }
  function append(role, who, text) {
    const el = document.createElement('div');
    el.className = 'msg ' + role;
    el.innerHTML = '<b>' + who + '：</b>' + text;
    document.getElementById('chat').appendChild(el);
  }
</script>
</body>
</html>
"""


def _load_env(path: Path) -> dict:
    env = {}
    if not path.exists():
        return env
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, v = line.split("=", 1)
        env[k.strip()] = v.strip().strip('"').strip("'")
    return env


def _llm_status(env: dict) -> str:
    if env.get("OPENAI_API_KEY"):
        return f"已配置 ({env.get('OPENAI_BASE_URL', 'https://api.openai.com/v1')} / {env.get('OPENAI_MODEL', 'gpt-4o-mini')})"
    return "未配置 API key（demo 模式：不调用云端 LLM）"


def _call_llm(env: dict, system_prompt: str, user_msg: str) -> str:
    if not env.get("OPENAI_API_KEY"):
        # Demo fallback: extract the first non-empty line from the system prompt's
        # safety section so the user sees something.
        return "（demo 模式：未配置 OPENAI_API_KEY。请在 .env 里设置后重启 mom-chat。）"

    try:
        import urllib.request
    except Exception:
        return "（urllib 不可用，无法调用 LLM）"

    base = env.get("OPENAI_BASE_URL", "https://api.openai.com/v1").rstrip("/")
    model = env.get("OPENAI_MODEL", "gpt-4o-mini")
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": system_prompt[:6000]},
            {"role": "user", "content": user_msg},
        ],
        "temperature": 0.7,
    }
    req = urllib.request.Request(
        f"{base}/chat/completions",
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {env['OPENAI_API_KEY']}",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            data = json.loads(resp.read().decode("utf-8"))
    except Exception as exc:
        return f"（LLM 调用失败：{exc}）"
    try:
        return data["choices"][0]["message"]["content"]
    except (KeyError, IndexError):
        return "（LLM 响应格式异常）"


def _load_bot(bot_dir: Path) -> dict:
    prompt_path = bot_dir / "bot" / "MOM_BOT_SYSTEM_PROMPT.md"
    raw_path = bot_dir / "raw" / "mom_chat_full.jsonl"
    system_prompt = prompt_path.read_text(encoding="utf-8") if prompt_path.exists() else ""
    raw_excerpt_lines: List[str] = []
    if raw_path.exists():
        for i, line in enumerate(raw_path.read_text(encoding="utf-8").splitlines()):
            if not line.strip():
                continue
            raw_excerpt_lines.append(line)
            if i >= 30:
                break
    return {"system_prompt": system_prompt, "raw_excerpt": "\n".join(raw_excerpt_lines)}


def run_mom_chat_server(bot_dir: str, host: str = "127.0.0.1", port: int = 5050) -> None:
    if Flask is None:
        raise RuntimeError("flask is not installed; run `pip install -e .[dev]` first")

    bot_path = Path(bot_dir)
    if not (bot_path / "bot" / "MOM_BOT_SYSTEM_PROMPT.md").exists():
        raise SystemExit(
            f"MOM_BOT_SYSTEM_PROMPT.md not found under {bot_path}. "
            "Run `wememoir mom-bot <raw.jsonl> --out <bot_dir>` first."
        )

    env = _load_env(Path(".env"))
    loaded = _load_bot(bot_path)
    system_prompt = loaded["system_prompt"]
    raw_excerpt = loaded["raw_excerpt"]
    history: List[dict] = []

    app = Flask("wememoir_mom_chat")

    @app.get("/")
    def index():
        excerpt = system_prompt[:1200] + ("\n..." if len(system_prompt) > 1200 else "")
        return render_template_string(
            INDEX_HTML,
            llm_status=_llm_status(env),
            history=history,
            system_prompt_excerpt=excerpt,
        )

    @app.post("/api/chat")
    def chat():
        payload = request.get_json(force=True, silent=True) or {}
        user_msg = (payload.get("message") or "").strip()
        if not user_msg:
            return jsonify({"reply": ""})
        history.append({"role": "me", "who": "我", "text": user_msg})
        reply = _call_llm(env, system_prompt, user_msg)
        history.append({"role": "mom", "who": "妈", "text": reply})
        return jsonify({"reply": reply})

    @app.get("/api/health")
    def health():
        return jsonify({"ok": True, "llm_configured": bool(env.get("OPENAI_API_KEY"))})

    print(f"[wememoir] mom-chat running on http://{host}:{port}")
    app.run(host=host, port=port, debug=False)
