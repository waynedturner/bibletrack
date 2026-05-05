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

Run the strict one-day workflow:

```bash
python ingest_into_cortex.py --date 4-19 --translation nkjv
```

Update ingestion state directly:

```bash
python ingestion_state.py update --date 4-19 --content-hash abc123
```

Check ingestion status:

```bash
python ingestion_state.py status --date 4-19
python ingestion_state.py status --start 4-1 --end 4-7
```

## What it does

1. Fetches one BibleTrack page by `date_key` and `translation`
2. Parses commentary sections
3. Removes verse-body-like quote content while preserving commentary
4. Preserves Bible references, links, and source URL
5. Creates deterministic hashes and canonical IDs
6. Runs entity extraction for that one day first
7. Runs structural ingest for that same one day second
8. Writes both payload JSON files into `~/.bibletrack/tmp`

The strict workflow is one day per invocation. `ingest_into_cortex.py` is the normal entrypoint because it parses the page once and reuses the same day document for both extraction and structural ingest.
Ingestion state is recorded in `~/.bibletrack/ingestion.sqlite3` only after the actual Cortex tool calls complete successfully, not during payload generation.
Entity extraction must normalize repeated mentions to canonical labels/IDs and collapse aliases or spelling variants before linking.
The Cortex adapter also strips whitespace, removes duplicate entity labels, and stamps normalization metadata before emitting payload JSON.
Single dates print one status word; ranges print a compact `present/total` count.

## Determinism

Deterministic IDs and content hash are generated from ordered stable fields.
Rerunning with unchanged source content yields identical IDs and hashes.
