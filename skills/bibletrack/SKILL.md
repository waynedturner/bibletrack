---
name: bibletrack
description: Ingests BibleTrack daily commentary pages into Cortex memory. Use when you need to store or update BibleTrack summaries, readings, and commentary for a specific date and translation.
---

# bibletrack skill

## Purpose

Ingest one BibleTrack daily commentary page at a time into Cortex memory structures. Note that the commentary prose is translation-agnostic as it only references verses without quoting them. The supported workflow is strict: one day per run, with entity extraction and structural ingest executed successively for the same date.

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
4. Remove Bible verse-body-like blocks
5. Preserve commentary prose, Bible references, links, and source URL
6. Build deterministic section canonical IDs (translation-agnostic) and document hash
7. Run `cortex.extract_entities` for that single day first so the model can identify `Person`, `Place`, `Theme`, and `BibleReference` from raw commentary text.
8. Run `cortex.resolve_entities` for that same day second so the model can map entity mentions to canonical IDs, collapse aliases, and prefer batch graph links over one-off links.
9. Emit structural memory payloads through `CortexMCPAdapter` after resolution for the same day.
10. The adapter must normalize entity-bearing payloads by stripping whitespace, removing duplicates, and stamping canonicalization metadata before emitting tool JSON.
11. Execute the Cortex tool calls required by the generated extract, resolve, and structural payloads for that same day.
12. Record ingestion state in `~/.bibletrack/ingestion.sqlite3` only after those Cortex tool calls complete successfully.

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

Prints one JSON summary for the strict one-day workflow, including both the extraction payload file and the structural ingest payload file. The day is parsed once and reused for both outputs.

## Status

Use `ingestion_state.py status` to query the SQLite state store with minimal output.

- `--date 4-19` prints a single status word.
- `--start 4-1 --end 4-7` prints a compact `present/total` count.

Use `ingest_into_cortex.py` when you need the strict one-day workflow. It parses the page once and runs entity extraction and structural ingest successively for the same date.

Use `ingestion_state.py update` when the actual Cortex tool calls have completed successfully and you need to record or refresh state.
