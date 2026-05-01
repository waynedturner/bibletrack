from __future__ import annotations

import argparse
import json
from pathlib import Path

from models import DayDocument
from parser import parse_day


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


def main() -> None:
    arg_parser = argparse.ArgumentParser(description="Generate BibleTrack entity extraction requests")
    arg_parser.add_argument("--date", required=True, help="BibleTrack date key, e.g. 4-19")
    arg_parser.add_argument("--translation", default="nkjv", help="Translation key (used for fetch only), defaults to nkjv")
    arg_parser.add_argument(
        "--out-dir",
        default=None,
        help="Directory for generated payload JSON, defaults to ~/.bibletrack/tmp",
    )
    args = arg_parser.parse_args()

    day_doc = parse_day(date_key=args.date, translation=args.translation)

    out_dir = Path(args.out_dir) if args.out_dir else Path.home() / ".bibletrack" / "tmp"
    if not out_dir.is_absolute():
        out_dir = Path.cwd() / out_dir
    out_dir.mkdir(parents=True, exist_ok=True)

    payloads = build_extraction_payloads(day_doc)
    payload_file = out_dir / f"entity-extraction-{args.translation.lower()}-{args.date}.json"
    payload_file.write_text(json.dumps(payloads, indent=2, ensure_ascii=False), encoding="utf-8")

    print(
        json.dumps(
            {
                "date": args.date,
                "status": "entity_extraction_requests_generated",
                "payload_file": str(payload_file),
                "content_hash": day_doc.content_hash,
            },
            indent=2,
            ensure_ascii=False,
        )
    )


if __name__ == "__main__":
    main()
