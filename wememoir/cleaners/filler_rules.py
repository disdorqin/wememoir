from __future__ import annotations

import re

_FILLER_TOKENS = ["嗯+", "啊+", "哦+", "额+", "哈+", "h+", "6+", "草+", "笑死+"]
_FILLER_PATTERN = re.compile("^(" + "|".join(_FILLER_TOKENS) + ")+$")
_PUNCTUATION = "，。？！,.;:!?~～…、 \t\n\r"


def is_filler(content: str) -> bool:
    """判断一条消息是否只是无意义语气词/刷屏。

    如果消息在去标点空格后仅由语气词（及其重复）组成，则视为 filler。
    """
    text = content.strip()
    if not text:
        return True
    cleaned = "".join(ch for ch in text if ch not in _PUNCTUATION)
    if not cleaned:
        return True
    return bool(_FILLER_PATTERN.match(cleaned))
