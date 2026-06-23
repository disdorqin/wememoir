"""Mom-style comfort bot generator.

Pipeline::

    raw jsonl  ->  raw/        (verbatim copy + Markdown)
               ->  profile/    (voice profile, phrases, response patterns, memory map)
               ->  bot/        (system prompt, character card, AGENTS.md)

Hard rules baked into the system prompt:

* The bot must NOT pretend to be the user's real mother in the real world.
* It must NOT claim to be physically present with the user.
* It must NOT fabricate facts that are not in the chat log.
* In a crisis it must suggest real people / professional support.
* The raw chat log is preserved byte-for-byte; this module never mutates it.
"""

from __future__ import annotations

from .bot_builder import build_mom_bot
from .chat_server import run_mom_chat_server
from .phrase_extractor import extract_phrases
from .prompt_builder import build_system_prompt
from .response_patterns import extract_response_patterns
from .voice_analyzer import build_voice_profile

__all__ = [
    "build_mom_bot",
    "build_system_prompt",
    "build_voice_profile",
    "extract_phrases",
    "extract_response_patterns",
    "run_mom_chat_server",
]
