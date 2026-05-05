from __future__ import annotations

import argparse
import json
from pathlib import Path

from extract_entities import (
    build_day_extraction_payload,
    build_day_resolution_payload,
)
from models import DayDocument
from parser import parse_day
from summarizer import consolidate_day_prose, summarize_day


def build_daily_commentary_payload(day_doc: DayDocument) -> dict:
    """The full cleaned prose archive. Hidden from default search to prevent flooding."""
    return {
        "memory_type": "note",
        "id": f"bibletrack:{day_doc.reading_plan_key}:daily-commentary",
        "content": consolidate_day_prose(day_doc),
        "tags": f"bibletrack,commentary,{day_doc.reading_plan_key}",
        "hidden": True,  # Prevent context flooding
        "retention_policy": "protected",  # Prevent decay of canon commentary
        "metadata": {
            "source_url": day_doc.source_url,
            "translation": day_doc.translation,
            "reading_refs": day_doc.reading_refs,
            "content_hash": day_doc.content_hash,
        },
    }


def build_daily_summary_payload(day_doc: DayDocument) -> dict:
    """Compact summary for efficient search and high-level recall."""
    return {
        "memory_type": "summary",
        "id": f"bibletrack:{day_doc.reading_plan_key}:daily-summary",
        "content": summarize_day(day_doc),
        "tags": f"bibletrack,summary,{day_doc.reading_plan_key}",
        "retention_policy": "protected",  # Prevent decay of canon commentary
        "metadata": {
            "source_url": day_doc.source_url,
            "translation": day_doc.translation,
            "content_hash": day_doc.content_hash,
        },
    }


def build_daily_index_payload(day_doc: DayDocument) -> dict:
    """Compact visible index that preserves graph anchors without flooding search."""
    section_lines: list[str] = []
    for section in day_doc.sections:
        refs = f"refs: {', '.join(section.bible_references)}" if section.bible_references else ""
        section_lines.append(f"- {section.title}{': ' + refs if refs else ''}")

    content_lines = [
        f"BibleTrack {day_doc.reading_plan_key} ({day_doc.translation.upper()})",
        f"Reading refs: {', '.join(day_doc.reading_refs) or 'none'}",
        "Sections:",
        *section_lines,
    ]

    return {
        "memory_type": "note",
        "id": f"bibletrack:{day_doc.reading_plan_key}:daily-index",
        "content": "\n".join(content_lines),
        "tags": f"bibletrack,index,{day_doc.reading_plan_key}",
        "retention_policy": "protected",
        "metadata": {
            "source_url": day_doc.source_url,
            "translation": day_doc.translation,
            "content_hash": day_doc.content_hash,
        },
    }


def build_daily_links(day_doc: DayDocument) -> list[dict]:
    links: list[dict] = [
        {
            "tool": "cortex.link",
            "payload": {
                "source_id": f"bibletrack:{day_doc.reading_plan_key}:daily-summary",
                "target_id": f"bibletrack:{day_doc.reading_plan_key}:daily-commentary",
                "relation": "summarizes",
                "retention_policy": "protected",
            },
        },
        {
            "tool": "cortex.link",
            "payload": {
                "source_id": f"bibletrack:{day_doc.reading_plan_key}:daily-index",
                "target_id": f"bibletrack:{day_doc.reading_plan_key}:daily-commentary",
                "relation": "indexes",
                "retention_policy": "protected",
            },
        },
    ]

    return links


def build_daily_payloads(day_doc: DayDocument) -> list[dict]:
    return [
        {"tool": "cortex.store", "payload": build_daily_commentary_payload(day_doc)},
        {"tool": "cortex.store", "payload": build_daily_summary_payload(day_doc)},
        {"tool": "cortex.store", "payload": build_daily_index_payload(day_doc)},
        *build_daily_links(day_doc),
    ]


def write_day_outputs(
    day_doc: DayDocument,
    translation: str,
    date: str,
    out_dir: str | Path | None = None,
) -> dict:
    resolved_out_dir = Path(out_dir) if out_dir is not None else Path.home() / ".bibletrack" / "tmp"
    if not resolved_out_dir.is_absolute():
        resolved_out_dir = Path.cwd() / resolved_out_dir
    resolved_out_dir.mkdir(parents=True, exist_ok=True)

    extraction_payload = build_day_extraction_payload(day_doc)
    extraction_file = resolved_out_dir / f"entity-extract-{translation.lower()}-{date}.json"
    extraction_file.write_text(json.dumps([extraction_payload], indent=2, ensure_ascii=False), encoding="utf-8")

    resolution_payload = build_day_resolution_payload(day_doc)
    resolution_file = resolved_out_dir / f"entity-resolve-{translation.lower()}-{date}.json"
    resolution_file.write_text(json.dumps([resolution_payload], indent=2, ensure_ascii=False), encoding="utf-8")

    payloads = build_daily_payloads(day_doc)
    payload_file = resolved_out_dir / f"payloads-{translation.lower()}-{date}.json"
    payload_file.write_text(json.dumps(payloads, indent=2, ensure_ascii=False), encoding="utf-8")

    return {
        "date": date,
        "status": "extraction_resolution_and_payloads_generated",
        "extraction_file": str(extraction_file),
        "resolution_file": str(resolution_file),
        "payload_file": str(payload_file),
        "content_hash": day_doc.content_hash,
    }


def main() -> None:
    arg_parser = argparse.ArgumentParser(description="Ingest one BibleTrack commentary day into Cortex")
    arg_parser.add_argument("--date", required=True, help="BibleTrack date key, e.g. 4-19")
    arg_parser.add_argument("--translation", default="nkjv", help="Translation key (used for fetch only), defaults to nkjv")
    arg_parser.add_argument(
        "--out-dir",
        default=None,
        help="Directory for generated payload JSON, defaults to ~/.bibletrack/tmp",
    )
    args = arg_parser.parse_args()

    day_doc = parse_day(date_key=args.date, translation=args.translation)
    print(
        json.dumps(
            write_day_outputs(day_doc, args.translation, args.date, args.out_dir),
            indent=2,
            ensure_ascii=False,
        )
    )


if __name__ == "__main__":
    main()
