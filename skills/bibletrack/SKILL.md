---
name: bibletrack
description: Ingests BibleTrack daily commentary pages into Cortex memory. Use when you need to store or update BibleTrack summaries, readings, and commentary for a specific date and translation.
---

# bibletrack skill

## Purpose

Ingest one BibleTrack daily commentary page at a time into Cortex memory structures. Note that the commentary prose is translation-agnostic as it only references verses without quoting them.

## Prerequisites

- Cortex MCP tools must be installed and available in the Codex environment.
- Do not use this skill without the `mcp__cortex__` tool namespace.

## Inputs

- `--date` (example: `4-19`)
- `--translation` (optional, defaults to `nkjv`. Used only for fetching the source page.)

## Source format

`https://www.bibletrack.org/summary2/{translation}/{date_key}.html`

## Pipeline

1. Build URL from input args
2. Fetch and parse HTML with BeautifulSoup
3. Extract top reading refs and section headings
4. **Entity Extraction:** Use the separate extraction step to emit one `cortex.extract_entities` request per day so the model can identify `Person`, `Place`, `Theme`, and `BibleReference` from raw commentary text.
5. **Entity Resolution:** Tell the model to use the requested entity types to determine linking, and prefer batch graph links over one-off links. Resolve extracted entities downstream through Cortex so canonical IDs are model-driven, not hardcoded.
6. Remove Bible verse-body-like blocks
7. Preserve commentary prose, Bible references, links, and source URL
8. Build deterministic section canonical IDs (translation-agnostic) and document hash
9. Emit structural memory payloads through `CortexMCPAdapter`.
10. Record ingestion state in `~/.bibletrack/ingestion.sqlite3`.

## Memory objects created per section

- For ALL memory retention_policy should be 'protected'
- detail memory (segmented, translation-agnostic)
- summary memory (summarizes detail)
- index memory (indexes detail)

## Archive objects created per day

- note memory (full original commentary prose, as-is, translation-agnostic)

## Linking

- summary `summarizes` detail
- index `indexes` detail

## Output

Prints ingestion summary JSON with counts and content hash.

## Status

Use `ingestion_state.py status` to query the SQLite state store with minimal output.

- `--date 4-19` prints a single status word.
- `--start 4-1 --end 4-7` prints a compact `present/total` count.

Use `ingestion_state.py update` when you need to record or refresh state without running the full ingest.
