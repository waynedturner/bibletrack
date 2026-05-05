from __future__ import annotations

from models import DayDocument


def build_day_extraction_payload(day_doc: DayDocument) -> dict:
    """Detect entities from text only for the whole day."""
    return {
        "tool": "cortex.extract_entities",
        "payload": {
            "source_id": f"bibletrack:{day_doc.reading_plan_key}:entity-extract",
            "mode": "text_only",
            "entity_types": ["Person", "Place", "Theme", "BibleReference"],
            "instructions": [
                "Detect entities from the section text only.",
                "Do not assign canonical IDs in this step.",
                "Return compact structured JSON grouped by section with raw entity mentions and evidence.",
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
                "retention_policy": "protected",
            },
        },
    }


def build_extraction_payloads(day_doc: DayDocument) -> list[dict]:
    return [build_day_extraction_payload(day_doc)]


def build_day_resolution_payload(day_doc: DayDocument) -> dict:
    """Resolve extracted entity mentions to canonical IDs for the whole day."""
    return {
        "tool": "cortex.resolve_entities",
        "payload": {
            "source_id": f"bibletrack:{day_doc.reading_plan_key}:entity-resolve",
            "entity_types": ["Person", "Place", "Theme", "BibleReference"],
            "preferred_link_mode": "batch",
            "entity_resolution": "normalize",
            "instructions": [
                "Resolve extracted entity mentions to canonical entities and IDs.",
                "Collapse aliases, spelling variants, and duplicate referents.",
                "Prefer the canonical label already used in the day when the same referent appears multiple times.",
                "Prefer batch graph links over emitting one-off links for individual mentions.",
                "Return compact structured JSON grouped by section with canonical entities and graph links separated.",
                "Infer links between sections, entities, and Bible references when the text supports them.",
                "Do not emit duplicate entities for the same referent.",
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
                "retention_policy": "protected",
            },
        },
    }


def build_resolution_payloads(day_doc: DayDocument) -> list[dict]:
    return [build_day_resolution_payload(day_doc)]
