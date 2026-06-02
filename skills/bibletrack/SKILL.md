---
name: bibletrack
description: Ingests BibleTrack daily commentary pages and special study topics into Cortex memory. Use when you need to store or update BibleTrack summaries, readings, and commentary for a specific date or topic.
---

# bibletrack skill

## Purpose

Ingest BibleTrack daily commentary and special study topics into Cortex memory structures. Note that the prose is translation-agnostic as it only references verses without quoting them. 

## Prerequisites

- Cortex MCP tools must be installed and available in the Codex environment.
- Do not use this skill without the `mcp__cortex__` tool namespace.
- **Mandatory:** All stored memories must use `retention_policy: "protected"`. (Note: This requires the `memory.protect` scope).

## Inputs

### Daily Commentary
- `--date` (example: `4-19`)
- `--translation` (optional, defaults to `nkjv`. Used only for fetching the source page.)

### Special Topics
- Special topics are located in `notes/resource/misc/**/*.html`.
- Use `ingest_topic.py --file [path]` to process these.

## Pipeline

### 1. Daily Ingestion
1. Build URL from input args
2. Fetch and parse HTML with BeautifulSoup
3. Extract top reading refs and section headings
4. Remove Bible verse-body-like blocks
5. Preserve commentary prose, Bible references, links, and source URL
6. Build deterministic section canonical IDs (translation-agnostic) and document hash
7. Run `cortex.extract_entities` for that single day first.
8. Run `cortex.resolve_entities` for that same day second.
9. Emit structural memory payloads (`detail`, `summary`, `index`) with `retention_policy: "protected"`.
10. Execute the Cortex tool calls.
11. Record ingestion state in `~/.bibletrack/ingestion.sqlite3`.

### 2. Special Topics Ingestion
1. Use `topic_parser.py` (called via `ingest_topic.py`) to convert the HTML article into clean markdown prose.
2. Follow the same `extract_entities` and `resolve_entities` workflow as daily commentary.
3. Store `detail`, `summary`, and `index` memories for the topic.
4. All memories MUST use `retention_policy: "protected"`.
5. Establish graph links (`summarizes`, `indexes`, `references_person`, etc.).

## Memory objects created per section/topic

- `detail` memory (prose, hidden=true)
- `summary` memory (summarizes detail, searchable)
- `index` memory (indexes detail, navigational map)
- **ALL** must have `retention_policy: "protected"`

## Linking

- `summary` `summarizes` `detail`
- `index` `indexes` `detail`
- `index` `references_person` `[resolved_person_id]`
- `index` `references_place` `[resolved_place_id]`

## Status

Use `ingestion_state.py status` to query the SQLite state store with minimal output.

- `--date 4-19` prints a single status word.
- `--start 4-1 --end 4-7` prints a compact `present/total` count.

## Tools

- `ingest_into_cortex.py`: Orchestrates daily commentary ingestion.
- `ingest_topic.py`: Orchestrates special topic ingestion.
- `topic_parser.py`: Implementation of HTML-to-prose conversion for topics.
- `ingestion_state.py`: Manages local ingestion tracking.
