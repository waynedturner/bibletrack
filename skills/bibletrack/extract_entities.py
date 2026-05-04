from __future__ import annotations

from models import DayDocument


def build_day_extraction_payload(day_doc: DayDocument) -> dict:
    """Request LLM-driven entity extraction and batch graph linking for the whole day."""
    return {
        "tool": "cortex.extract_entities",
        "payload": {
            "source_id": f"bibletrack:{day_doc.reading_plan_key}:entity-batch",
            "entity_types": ["Person", "Place", "Theme", "BibleReference"],
            "preferred_link_mode": "batch",
            "instructions": [
                "Use the requested entity types to decide what should be linked.",
                "Prefer batch graph links over emitting one-off links for individual mentions.",
                "Return compact structured JSON grouped by section, with entities and graph links separated.",
                "Infer links between sections, entities, and Bible references when the text supports them.",
            ],
            "sections": [
                {
                    "section_id": section.canonical_id,
                    "title": section.title,
                    "text": section.commentary_text,
                    "bible_references": section.bible_references,
                }
                for section in day_doc.sections
            ],
            "context": {
                "reading_plan_key": day_doc.reading_plan_key,
                "source_url": day_doc.source_url,
                "translation": day_doc.translation,
            },
        },
    }


def build_extraction_payloads(day_doc: DayDocument) -> list[dict]:
    return [build_day_extraction_payload(day_doc)]
