from __future__ import annotations

import argparse
import json
from pathlib import Path

from cortex_mcp_adapter import CortexMCPAdapter
from models import DayDocument, Section
from parser import parse_day
from summarizer import summarize


def build_detail_payload(day_doc: DayDocument, section: Section) -> dict:
    return {
        "memory_type": "detail",
        "canonical_id": section.canonical_id,
        "title": section.title,
        "content": section.commentary_text,
        "metadata": {
            "immutable": True,
            "decay_allowed": False,
            "intent_preserving": True,
            "source_url": day_doc.source_url,
            "translation": day_doc.translation,
            "reading_plan_key": day_doc.reading_plan_key,
            "semantic_date": None,
            "refs": section.bible_references,
            "links": [link.model_dump() for link in section.links],
        },
    }


def build_summary_payload(section: Section) -> dict:
    return {
        "memory_type": "summary",
        "canonical_id": f"{section.canonical_id}:summary",
        "content": summarize(section.commentary_text),
    }


def build_index_payload(section: Section) -> dict:
    return {
        "memory_type": "index",
        "canonical_id": f"{section.canonical_id}:index",
        "content": {
            "title": section.title,
            "refs": section.bible_references,
            "people": section.people,
            "places": section.places,
            "themes": section.themes,
        },
    }


def main() -> None:
    arg_parser = argparse.ArgumentParser(description="Ingest one BibleTrack commentary day into Cortex")
    arg_parser.add_argument("--date", required=True, help="BibleTrack date key, e.g. 4-19")
    arg_parser.add_argument("--translation", default="nkjv", help="Translation key (used for fetch only), defaults to nkjv")
    args = arg_parser.parse_args()

    day_doc = parse_day(date_key=args.date, translation=args.translation)

    # Use the project's temporary directory for script outputs
    out_dir = Path("/Users/stephenturner/.gemini/tmp/bibletrack/out")
    out_dir.mkdir(parents=True, exist_ok=True)
    out_file = out_dir / f"{args.translation.lower()}-{args.date}.json"
    out_file.write_text(json.dumps(day_doc.model_dump(), indent=2, ensure_ascii=False), encoding="utf-8")

    adapter = CortexMCPAdapter()
    detail_count = 0
    summary_count = 0
    index_count = 0

    # Archive original commentary as a single note (translation-agnostic)
    full_original_prose = "\n\n".join(s.commentary_text for s in day_doc.sections)
    adapter.upsert_memory({
        "memory_type": "note",
        "canonical_id": f"bibletrack:{day_doc.reading_plan_key}:full-commentary",
        "content": full_original_prose,
        "metadata": {
            "source_url": day_doc.source_url,
            "translation": day_doc.translation,
            "date_key": day_doc.reading_plan_key,
            "is_original_source": True
        }
    })

    for section in day_doc.sections:
        detail_id = adapter.upsert_memory(build_detail_payload(day_doc, section))
        detail_count += 1

        summary_id = adapter.upsert_memory(build_summary_payload(section))
        summary_count += 1

        index_id = adapter.upsert_memory(build_index_payload(section))
        index_count += 1

        adapter.link_memories(summary_id, detail_id, "summarizes")
        adapter.link_memories(index_id, detail_id, "indexes")

    print(
        json.dumps(
            {
                "source_url": day_doc.source_url,
                "sections_ingested": len(day_doc.sections),
                "detail_created": detail_count,
                "summary_created": summary_count,
                "index_created": index_count,
                "content_hash": day_doc.content_hash,
            },
            indent=2,
            ensure_ascii=False,
        )
    )


if __name__ == "__main__":
    main()
