from __future__ import annotations

import argparse
import json
from pathlib import Path

from models import TopicDocument
from topic_parser import parse_topic_file


def build_topic_detail_payload(topic_doc: TopicDocument) -> dict:
    """The full cleaned prose of the special topic."""
    return {
        "memory_type": "note",
        "id": f"{topic_doc.id}:detail",
        "content": topic_doc.content,
        "tags": f"bibletrack,topic,{topic_doc.slug},detail",
        "hidden": True,
        "retention_policy": "protected",
        "metadata": {
            "title": topic_doc.title,
            "source_url": topic_doc.source_url,
            "content_hash": topic_doc.content_hash,
        },
    }


def build_topic_summary_payload(topic_doc: TopicDocument) -> dict:
    """Compact summary of the topic."""
    # For now, we'll just use the first paragraph or a placeholder
    # The actual summarization would ideally happen via a model call,
    # but we'll follow the pattern of generating a payload that CAN be stored.
    # Actually, in the topic case, I'll just use the title and source for the summary
    # and let the user/model refine it.
    return {
        "memory_type": "summary",
        "id": f"{topic_doc.id}:summary",
        "content": f"Study topic covering {topic_doc.title}.",
        "tags": f"bibletrack,topic,{topic_doc.slug},summary",
        "retention_policy": "protected",
        "metadata": {
            "source_url": topic_doc.source_url,
            "content_hash": topic_doc.content_hash,
        },
    }


def build_topic_index_payload(topic_doc: TopicDocument) -> dict:
    """Compact navigational index for the topic."""
    return {
        "memory_type": "note",
        "id": f"{topic_doc.id}:index",
        "content": f"BibleTrack Study Topic: {topic_doc.title}\nSource: {topic_doc.source_url}",
        "tags": f"bibletrack,topic,{topic_doc.slug},index",
        "retention_policy": "protected",
        "metadata": {
            "source_url": topic_doc.source_url,
            "content_hash": topic_doc.content_hash,
        },
    }


def build_topic_links(topic_doc: TopicDocument) -> list[dict]:
    return [
        {
            "tool": "cortex.link",
            "payload": {
                "source_id": f"{topic_doc.id}:summary",
                "target_id": f"{topic_doc.id}:detail",
                "relation": "summarizes",
                "retention_policy": "protected",
            },
        },
        {
            "tool": "cortex.link",
            "payload": {
                "source_id": f"{topic_doc.id}:index",
                "target_id": f"{topic_doc.id}:detail",
                "relation": "indexes",
                "retention_policy": "protected",
            },
        },
    ]


def build_topic_payloads(topic_doc: TopicDocument) -> list[dict]:
    return [
        {"tool": "cortex.store", "payload": build_topic_detail_payload(topic_doc)},
        {"tool": "cortex.store", "payload": build_topic_summary_payload(topic_doc)},
        {"tool": "cortex.store", "payload": build_topic_index_payload(topic_doc)},
        *build_topic_links(topic_doc),
    ]


def main() -> None:
    arg_parser = argparse.ArgumentParser(description="Ingest BibleTrack special topics into Cortex")
    arg_parser.add_argument("--file", required=True, help="Path to the HTML topic file")
    arg_parser.add_argument(
        "--out-dir",
        default=None,
        help="Directory for generated payload JSON, defaults to ~/.bibletrack/tmp",
    )
    args = arg_parser.parse_args()

    file_path = Path(args.file)
    if not file_path.exists():
        print(f"Error: File {file_path} not found.")
        return

    topic_doc = parse_topic_file(file_path)
    
    resolved_out_dir = Path(args.out_dir) if args.out_dir is not None else Path.home() / ".bibletrack" / "tmp"
    resolved_out_dir.mkdir(parents=True, exist_ok=True)

    # Simplified extraction/resolution payloads for topics
    extract_payload = {
        "tool": "cortex.extract_entities",
        "payload": {
            "text": topic_doc.content,
            "labels": "Person, Place, Theme, BibleReference"
        }
    }
    extract_file = resolved_out_dir / f"topic-extract-{topic_doc.slug}.json"
    extract_file.write_text(json.dumps([extract_payload], indent=2, ensure_ascii=False), encoding="utf-8")

    payloads = build_topic_payloads(topic_doc)
    payload_file = resolved_out_dir / f"topic-payloads-{topic_doc.slug}.json"
    payload_file.write_text(json.dumps(payloads, indent=2, ensure_ascii=False), encoding="utf-8")

    result = {
        "topic": topic_doc.title,
        "status": "extraction_and_payloads_generated",
        "extraction_file": str(extract_file),
        "payload_file": str(payload_file),
        "content_hash": topic_doc.content_hash,
    }
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
