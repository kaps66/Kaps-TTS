"""Bilingual phonemizer with vocal event support."""
import re
from typing import List, Tuple

VOCAL_EVENTS = {
    "(laugh)": "<|LAUGH|>",
    "(sigh)": "<|SIGH|>",
    "(cough)": "<|COUGH|>",
    "(clears throat)": "<|CLEAR_THROAT|>",
    "(breath)": "<|BREATH|>",
    "(pause)": "<|PAUSE|>",
}

EVENT_PATTERN = re.compile(
    r"\((laugh|sigh|cough|clears throat|breath|pause)\)", re.IGNORECASE
)


def phonemize(text: str, language: str = "en") -> List[str]:
    """Convert text to phoneme tokens with inline vocal events."""
    tokens = []
    parts = EVENT_PATTERN.split(text)

    for i, part in enumerate(parts):
        if i % 2 == 1:  # This is a captured vocal event
            key = f"({part.lower()})"
            if key in VOCAL_EVENTS:
                tokens.append(VOCAL_EVENTS[key])
            continue

        if not part.strip():
            continue

        if language == "zh":
            from pypinyin import pinyin, Style
            pys = pinyin(part, style=Style.TONE3)
            tokens.extend([p[0] for p in pys])
        else:
            from g2p_en import G2p
            g2p = G2p()
            tokens.extend(g2p(part))

    return tokens
