from __future__ import annotations

import re
import string
from collections import Counter
from datetime import datetime
from pathlib import Path

from ..models import Conversation, Message


_TEMPLATE_DIR = Path(__file__).with_name("templates")


def _render(template_text: str, data: dict) -> str:
    return string.Template(template_text).safe_substitute(data)


def _top_words(messages: list[Message], n: int = 10) -> list[str]:
    counter: Counter[str] = Counter()
    stopwords = set("的 了 是 我 你 在 和 就 不 人 有 都 个 上 也 很 到 说 要 去 可以 这个 会 好 吗 吧 呢 啊 那 这 他 她 它".split())
    pattern = re.compile(r"[\u4e00-\u9fa5]{2,4}")
    for m in messages:
        for w in pattern.findall(m.content):
            if w not in stopwords:
                counter[w] += 1
    return [w for w, _ in counter.most_common(n)]


def _avg_length(messages: list[Message]) -> float:
    if not messages:
        return 0.0
    return sum(len(m.content) for m in messages) / len(messages)


def _sample_messages(messages: list[Message], n: int = 5) -> list[str]:
    result: list[str] = []
    seen: set[str] = set()
    for m in messages:
        text = m.content.strip()
        if text and text not in seen and len(text) >= 5:
            seen.add(text)
            result.append(text)
            if len(result) >= n:
                break
    return result


def _collect_data(conversation: Conversation, skill_type: str) -> dict:
    all_msgs = conversation.messages
    self_msgs = [m for m in all_msgs if m.sender_type == "self"]
    other_msgs = [m for m in all_msgs if m.sender_type != "self"]

    target_msgs = self_msgs if skill_type == "self" else (other_msgs if skill_type == "contact" else all_msgs)

    time_range = "未知"
    if all_msgs:
        start = min(m.timestamp for m in all_msgs)
        end = max(m.timestamp for m in all_msgs)
        time_range = f"{start.strftime('%Y-%m-%d')} ~ {end.strftime('%Y-%m-%d')}"

    samples = _sample_messages(target_msgs, 5)
    examples = "\n".join(f"- {s}" for s in samples) if samples else "- （暂无示例）"

    style_notes = []
    avg = _avg_length(target_msgs)
    style_notes.append(f"平均消息长度约 {avg:.1f} 字。")
    top = _top_words(target_msgs, 5)
    if top:
        style_notes.append(f"常用词汇：{', '.join(top)}。")
    style = " ".join(style_notes)

    if skill_type == "contact":
        scenario = f"描述、模仿或以 {conversation.name} 的视角进行创作。"
        relationship = f"这是与 {conversation.name} 的{'群聊' if conversation.type == 'group' else '私聊'}，时间跨度 {time_range}。"
    elif skill_type == "self":
        scenario = "描述我的表达风格、语气、习惯用语，或代我起草回复。"
        relationship = f"从聊天记录中提炼出的我的表达风格，时间跨度 {time_range}。"
    else:
        scenario = "帮助整理、续写、润色聊天回忆录。"
        relationship = f"基于与 {conversation.name} 的聊天记录生成的回忆录助手，时间跨度 {time_range}。"

    return {
        "name": conversation.name,
        "type": conversation.type,
        "skill_type": skill_type,
        "participants": ", ".join(conversation.participants),
        "message_count": str(len(all_msgs)),
        "time_range": time_range,
        "scenario": scenario,
        "relationship": relationship,
        "facts": f"- 参与人：{', '.join(conversation.participants)}\n- 消息总数：{len(all_msgs)}\n- 时间范围：{time_range}",
        "style": style,
        "boundaries": (
            "- 不要调用任何外部 API 发送消息。\n"
            "- 不要推测、编造超出聊天记录的隐私信息。\n"
            "- 生成的内容仅用于本地整理与创作，不要上传云端或共享。\n"
            "- 如果对方明显不希望被记录的话题，应避免在示例中重复。"
        ),
        "examples": examples,
        "local_files": "- 导入的原始聊天记录 JSON\n- 清洗后的对话 Markdown\n- 生成的回忆录 Markdown",
    }


def _template_filename(skill_type: str, target: str) -> str:
    if target == "codex":
        return "codex_agents.md"
    if target == "cursor":
        return "cursor_rule.mdc"
    if target == "claude":
        return f"{skill_type}_skill.md"
    return f"{skill_type}_skill.md"


def build_skill(conversation: Conversation, skill_type: str, target: str, out_path: str) -> str:
    if skill_type not in ("contact", "self", "memoir"):
        raise ValueError(f"Unsupported skill type: {skill_type}")

    data = _collect_data(conversation, skill_type)
    template_name = _template_filename(skill_type, target)
    template_path = _TEMPLATE_DIR / template_name
    if not template_path.exists():
        # Fallback to generic markdown template for the skill type
        template_path = _TEMPLATE_DIR / f"{skill_type}_skill.md"

    template = template_path.read_text(encoding="utf-8")
    rendered = _render(template, data)

    p = Path(out_path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(rendered, encoding="utf-8")
    return rendered
