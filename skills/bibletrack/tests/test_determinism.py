import parser as parser_module


SAMPLE_HTML = """
<html>
<head><title>Mark 5:38-43</title></head>
<body>
  <h2>Raising a Daughter</h2>
  <p>Commentary body is stable for deterministic tests.</p>
  <a href="https://example.com/related">Related</a>
</body>
</html>
"""


def test_parse_day_is_deterministic(monkeypatch) -> None:
    monkeypatch.setattr(parser_module, "fetch_html", lambda _url: SAMPLE_HTML)
    doc1 = parser_module.parse_day("4-19", "nkjv")
    doc2 = parser_module.parse_day("4-19", "nkjv")

    assert doc1.content_hash == doc2.content_hash
    assert [s.canonical_id for s in doc1.sections] == [s.canonical_id for s in doc2.sections]
