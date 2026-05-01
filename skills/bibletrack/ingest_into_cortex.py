from __future__ import annotations

import argparse
import json
from pathlib import Path

from cortex_mcp_adapter import CortexMCPAdapter
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


def main() -> None:
    arg_parser = argparse.ArgumentParser(description="Ingest one BibleTrack commentary day into Cortex")
    arg_parser.add_argument("--date", required=True, help="BibleTrack date key, e.g. 4-19")
    arg_parser.add_argument("--translation", default="nkjv", help="Translation key (used for fetch only), defaults to nkjv")
    args = arg_parser.parse_args()

    day_doc = parse_day(date_key=args.date, translation=args.translation)

    # Use a consistent temporary directory for script outputs
    out_dir = Path("/Users/stephenturner/.gemini/tmp/bibletrack/out")
    out_dir.mkdir(parents=True, exist_ok=True)
    
    # Store tool payloads in a separate file for the agent to process quietly
    payloads = [
        {"tool": "cortex.store", "payload": build_daily_commentary_payload(day_doc)},
        {"tool": "cortex.store", "payload": build_daily_summary_payload(day_doc)},
        {
            "tool": "cortex.link", 
            "payload": {
                "source_id": f"bibletrack:{day_doc.reading_plan_key}:daily-summary",
                "target_id": f"bibletrack:{day_doc.reading_plan_key}:daily-commentary",
                "relation": "summarizes"
            }
        }
    ]
    
    payload_file = out_dir / f"payloads-{args.translation.lower()}-{args.date}.json"
    payload_file.write_text(json.dumps(payloads, indent=2, ensure_ascii=False), encoding="utf-8")

    print(
        json.dumps(
            {
                "date": args.date,
                "status": "payloads_generated_quietly",
                "payload_file": str(payload_file),
                "content_hash": day_doc.content_hash
            },
            indent=2,
            ensure_ascii=False,
        )
    )


if __name__ == "__main__":
    main()
