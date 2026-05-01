from __future__ import annotations

import re
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from models import DayDocument


def clean_prose(text: str) -> str:
    """Clean and normalize commentary prose while preserving all original text and tone."""
    # Remove excessive whitespace and normalize line breaks
    cleaned = re.sub(r"[ \t]+", " ", text).strip()
    return cleaned


def summarize(text: str) -> str:
    """Deterministic concise summary using first 3 sentences."""
    cleaned = clean_prose(text)
    if not cleaned:
        return ""
    # Split by sentence boundaries
    sentences = re.split(r"(?<=[.!?])\s+", cleaned)
    summary = " ".join(sentences[:3]).strip()
    return summary


def summarize_day(day_doc: DayDocument) -> str:
    """Aggregate summaries of all sections into a single compact daily summary."""
    summaries = []
    for section in day_doc.sections:
        summary_text = summarize(section.commentary_text)
        if summary_text:
            header = f"### {section.title}\n" if len(day_doc.sections) > 1 else ""
            summaries.append(f"{header}{summary_text}")
    
    return "\n\n".join(summaries)


def consolidate_day_prose(day_doc: DayDocument) -> str:
    """Consolidate the full cleaned prose of all sections into a single daily record."""
    prose_blocks = []
    for section in day_doc.sections:
        text = clean_prose(section.commentary_text)
        if text:
            header = f"### {section.title}\n"
            prose_blocks.append(f"{header}{text}")
    
    return "\n\n".join(prose_blocks)
