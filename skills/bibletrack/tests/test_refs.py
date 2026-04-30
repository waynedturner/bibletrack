from parser import extract_refs


def test_extract_refs_patterns() -> None:
    text = "John 11:1-57 Luke 17:11-19 1 Corinthians 15:51-53 Mark 5:38-43"
    refs = extract_refs(text)
    assert "John 11:1-57" in refs
    assert "Luke 17:11-19" in refs
    assert "1 Corinthians 15:51-53" in refs
    assert "Mark 5:38-43" in refs
