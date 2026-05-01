# bibletrack

Cortex MCP-backed one-day BibleTrack commentary ingestion skill.

## Prerequisites

- Cortex MCP tools must be installed and available in the Codex environment.
- This skill is not intended to run in an environment without the `mcp__cortex__` tool namespace.

## Install dependencies

```bash
pip install -r requirements.txt
```

## Run

Generate entity extraction requests:

```bash
python extract_entities.py --date 4-19 --translation nkjv
```

Generate daily commentary payloads:

```bash
python ingest_into_cortex.py --date 4-19 --translation nkjv
```

## What it does

1. Fetches one BibleTrack page by `date_key` and `translation`
2. Parses commentary sections
3. Removes verse-body-like quote content while preserving commentary
4. Preserves Bible references, links, and source URL
5. Creates deterministic hashes and canonical IDs
6. Writes output artifact JSON into `~/.bibletrack/tmp`
7. Emits detail/summary/index payloads

Entity extraction is a separate step so the model can decide people, places, themes, and references independently of the structural ingest pass.
The extraction request is batched by day and should instruct the model to use the entity types to determine linking and prefer batch graph links.
By default, both scripts write payload JSON into `~/.bibletrack/tmp`.

## Determinism

Deterministic IDs and content hash are generated from ordered stable fields.
Rerunning with unchanged source content yields identical IDs and hashes.
