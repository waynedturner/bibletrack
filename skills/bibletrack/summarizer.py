from __future__ import annotations

import re


def summarize(text: str) -> str:
    """Deterministic concise summary using first 3-4 sentences."""
    cleaned = re.sub(r"\s+", " ", text).strip()
    if not cleaned:
        return ""
    sentences = re.split(r"(?<=[.!?])\s+", cleaned)
    summary = " ".join(sentences[:4]).strip()
    return summary
