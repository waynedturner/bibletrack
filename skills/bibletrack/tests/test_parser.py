import parser as parser_module


SAMPLE_HTML = """
<html>
<head><title>John 11:1-57 Luke 17:11-19</title></head>
<body>
  <h2>Lazarus Dies</h2>
  <p>This commentary explains the setup and context. Jesus meets Martha and Mary in Bethany and Judea.</p>
  <blockquote>> 1 Now a certain man was sick, named Lazarus...</blockquote>
  <p>Application and analysis continue with practical notes.</p>
  <p>1 This numbered commentary point should remain in the final prose.</p>
  <a href="https://example.com/audio.mp3">Audio Version</a>
  <h2>Ten Lepers</h2>
  <p>Only one returned to give thanks and this is emphasized. Jesus shows mercy and healing.</p>
  <p>> 11 Now it happened as He went to Jerusalem...</p>
  <a href="/notes/today">Study Note</a>
</body>
</html>
"""


def test_parse_day_sections_links_and_filtering(monkeypatch) -> None:
    monkeypatch.setattr(parser_module, "fetch_html", lambda _url: SAMPLE_HTML)
    doc = parser_module.parse_day("4-19", "nkjv")

    assert len(doc.sections) == 2
    assert any("Lazarus Dies" == s.title for s in doc.sections)
    assert all("> 1 Now a certain man" not in s.commentary_text for s in doc.sections)
    assert any("1 This numbered commentary point should remain" in s.commentary_text for s in doc.sections)
    assert any("Application and analysis" in s.commentary_text for s in doc.sections)
    assert any(link.link_type == "audio" for link in doc.links)
    assert any(link.link_type == "note" for link in doc.links)
    assert "John 11:1-57" in doc.reading_refs
    first_section = next(section for section in doc.sections if section.title == "Lazarus Dies")
    assert first_section.people == []
    assert first_section.places == []
    assert first_section.themes == []


def test_parse_day_leaves_entities_for_llm(monkeypatch) -> None:
    monkeypatch.setattr(parser_module, "fetch_html", lambda _url: SAMPLE_HTML)
    doc = parser_module.parse_day("4-19", "nkjv")

    second_section = next(section for section in doc.sections if section.title == "Ten Lepers")
    assert second_section.people == []
    assert second_section.places == []
    assert second_section.themes == []
