# bibletrack skill

## Purpose

Ingest one BibleTrack daily commentary page at a time into Cortex memory structures.

## Prerequisites

- Cortex MCP tools must be installed and available in the Codex environment.
- Do not use this skill without the `mcp__cortex__` tool namespace.

## Inputs

- `--date` (example: `4-19`)
- `--translation` (example: `nkjv`)

## Source format

`https://www.bibletrack.org/summary2/{translation}/{date_key}.html`

## Pipeline

1. Build URL from input args
2. Fetch and parse HTML with BeautifulSoup
3. Extract top reading refs and section headings
4. Remove Bible verse-body-like blocks
5. Preserve commentary prose, Bible references, links, and source URL
6. Build deterministic section canonical IDs and document hash
7. Emit memory payloads through `CortexMCPAdapter`

## Memory objects created per section

- detail memory
- summary memory
- index memory

## Linking

- summary `summarizes` detail
- index `indexes` detail

## Output

Prints ingestion summary JSON with counts and content hash.
