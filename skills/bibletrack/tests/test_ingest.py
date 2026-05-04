import sqlite3

from models import DayDocument, Section, SourceLink
from extract_entities import build_day_extraction_payload, build_extraction_payloads
from ingest_into_cortex import build_daily_index_payload, build_daily_links, write_day_outputs
from ingestion_state import get_ingestion_range_status, get_ingestion_status, update_ingestion_state


def _day_doc() -> DayDocument:
    return DayDocument(
        source_url="https://www.bibletrack.org/summary2/nkjv/4-19.html",
        translation="nkjv",
        reading_plan_key="4-19",
        reading_refs=["John 11:1-57", "Luke 17:11-19"],
        links=[SourceLink(url="https://www.bibletrack.org/summary2/nkjv/4-19.html", link_text="source", link_type="source")],
        sections=[
            Section(
                canonical_id="bibletrack:4-19:lazarus-dies",
                title="Lazarus Dies",
                commentary_text="Jesus meets Martha and Mary in Bethany.",
                bible_references=["John 11:1-17"],
            )
        ],
        content_hash="abc123",
    )


def test_daily_index_payload_surfaces_refs() -> None:
    day_doc = _day_doc()
    payload = build_daily_index_payload(day_doc)

    assert payload["id"] == "bibletrack:4-19:daily-index"
    assert "refs: John 11:1-17" in payload["content"]


def test_day_extraction_payload_requests_llm_entities() -> None:
    day_doc = _day_doc()
    payload = build_day_extraction_payload(day_doc)

    assert payload["tool"] == "cortex.extract_entities"
    assert payload["payload"]["source_id"] == "bibletrack:4-19:entity-batch"
    assert payload["payload"]["entity_types"] == ["Person", "Place", "Theme", "BibleReference"]
    assert payload["payload"]["preferred_link_mode"] == "batch"
    assert any("Prefer batch graph links" in line for line in payload["payload"]["instructions"])
    assert payload["payload"]["sections"][0]["section_id"] == "bibletrack:4-19:lazarus-dies"
    assert "Jesus meets Martha and Mary in Bethany." in payload["payload"]["sections"][0]["text"]


def test_extraction_payload_batch_matches_sections() -> None:
    day_doc = _day_doc()
    payloads = build_extraction_payloads(day_doc)

    assert len(payloads) == 1
    assert payloads[0]["payload"]["context"]["reading_plan_key"] == "4-19"
    assert payloads[0]["payload"]["sections"][0]["title"] == "Lazarus Dies"


def test_daily_links_include_summary_and_index() -> None:
    day_doc = _day_doc()
    links = build_daily_links(day_doc)

    assert any(link["payload"]["relation"] == "summarizes" for link in links)
    assert any(link["payload"]["relation"] == "indexes" for link in links)


def test_update_ingestion_state_uses_sqlite(tmp_path) -> None:
    db_path = tmp_path / "ingestion.sqlite3"

    first_status = update_ingestion_state("4-1", "nkjv", "abc123", db_path=db_path)
    second_status = update_ingestion_state("4-1", "nkjv", "def456", db_path=db_path)

    assert first_status == "Ingested"
    assert second_status == "Re-ingest"

    with sqlite3.connect(db_path) as conn:
        row = conn.execute(
            "SELECT date, translation, status, content_hash FROM ingestion_state WHERE date = ? AND translation = ?",
            ("4-1", "nkjv"),
        ).fetchone()

    assert row == ("4-1", "nkjv", "Re-ingest", "def456")


def test_update_ingestion_state_accepts_explicit_status(tmp_path) -> None:
    db_path = tmp_path / "ingestion.sqlite3"

    status = update_ingestion_state("4-1", "nkjv", "abc123", db_path=db_path, status="Imported")

    assert status == "Imported"


def test_get_ingestion_status_returns_single_token(tmp_path) -> None:
    db_path = tmp_path / "ingestion.sqlite3"
    update_ingestion_state("4-1", "nkjv", "abc123", db_path=db_path)

    assert get_ingestion_status("4-1", db_path=db_path) == "Ingested"
    assert get_ingestion_status("4-2", db_path=db_path) == "Missing"


def test_get_ingestion_range_status_returns_compact_count(tmp_path) -> None:
    db_path = tmp_path / "ingestion.sqlite3"
    update_ingestion_state("4-1", "nkjv", "abc123", db_path=db_path)
    update_ingestion_state("4-2", "kiv", "def456", db_path=db_path)
    update_ingestion_state("4-4", "nkjv", "ghi789", db_path=db_path)

    assert get_ingestion_range_status("4-1", "4-4", db_path=db_path) == "3/4"


def test_write_day_outputs_generates_both_payloads_successively(tmp_path) -> None:
    day_doc = _day_doc()
    out_dir = tmp_path / "out"
    db_path = tmp_path / "ingestion.sqlite3"

    result = write_day_outputs(day_doc, "nkjv", "4-19", out_dir=out_dir, db_path=db_path)

    assert result["status"] == "extraction_and_payloads_generated"
    assert (out_dir / "entity-extraction-nkjv-4-19.json").exists()
    assert (out_dir / "payloads-nkjv-4-19.json").exists()
    assert get_ingestion_status("4-19", db_path=db_path) == "Ingested"
