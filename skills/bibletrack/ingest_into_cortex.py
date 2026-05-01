from __future__ import annotations

import argparse
import json
from pathlib import Path

from cortex_mcp_adapter import CortexMCPAdapter
from models import DayDocument, Section
from parser import parse_day
from summarizer import summarize


def build_archive_payload(day_doc: DayDocument) -> dict:
    full_prose = "\n\n".join([f"### {s.title}\n{s.commentary_text}" for s in day_doc.sections])
    return {
        "memory_type": "note",
        "id": f"bibletrack:{day_doc.reading_plan_key}:full-commentary",
        "content": full_prose,
        "tags": f"bibletrack,archive,{day_doc.reading_plan_key}",
        "source": "bibletrack_ingestor",
        "salience": 0.5,
        "hidden": True,
        "metadata": {
            "source_url": day_doc.source_url,
            "translation": day_doc.translation,
            "reading_refs": day_doc.reading_refs,
            "content_hash": day_doc.content_hash,
            "is_original_source": True
        },
    }


def build_summary_payload(section: Section) -> dict:
    return {
        "memory_type": "summary",
        "id": f"{section.canonical_id}:summary",
        "content": summarize(section.commentary_text),
        "tags": "bibletrack,summary",
    }


def main() -> None:
    arg_parser = argparse.ArgumentParser(description="Ingest one BibleTrack commentary day into Cortex")
    arg_parser.add_argument("--date", required=True, help="BibleTrack date key, e.g. 4-19")
    arg_parser.add_argument("--translation", default="nkjv", help="Translation key (used for fetch only), defaults to nkjv")
    args = arg_parser.parse_args()

    day_doc = parse_day(date_key=args.date, translation=args.translation)

    # Use a consistent temporary directory for script outputs
    out_dir = Path("/Users/stephenturner/.gemini/tmp/bibletrack/out")
    out_dir.mkdir(parents=True, exist_ok=True)
    out_file = out_dir / f"{args.translation.lower()}-{args.date}.json"
    out_file.write_text(json.dumps(day_doc.model_dump(), indent=2, ensure_ascii=False), encoding="utf-8")

    adapter = CortexMCPAdapter()
    
    # 1. Store full archive note (hidden by default)
    archive_id = adapter.upsert_memory(build_archive_payload(day_doc))

    for section in day_doc.sections:
        # 2. Store summary
        summary_id = adapter.upsert_memory(build_summary_payload(section))

        # 3. Link summary to archive
        adapter.link_memories(summary_id, archive_id, "summarizes")

    print(
        json.dumps(
            {
                "source_url": day_doc.source_url,
                "sections_ingested": len(day_doc.sections),
                "content_hash": day_doc.content_hash,
                "status": "payloads_generated"
            },
            indent=2,
            ensure_ascii=False,
        )
    )


if __name__ == "__main__":
    main()
