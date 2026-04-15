from __future__ import annotations

from datetime import datetime, timezone
from html import unescape
import json
import re
from pathlib import Path


SITE_URL = "https://www.bibletrack.org"
ROOT = Path(__file__).resolve().parent.parent
SEARCH_INDEX_PATH = ROOT / "search-index.json"
EXCLUDED_PATH_PARTS = {"notes/KJV Text/"}
STOP_WORDS = {
    "the", "and", "for", "that", "with", "this", "from", "your", "have", "are",
    "was", "were", "will", "into", "about", "there", "their", "them", "they",
    "then", "than", "when", "what", "which", "would", "could", "should", "also",
    "been", "being", "through", "after", "before", "more", "each", "such", "only",
    "not", "his", "her", "him", "you", "our", "out", "who", "why", "how", "where",
    "all", "but", "can", "did", "does", "had", "has", "may", "its", "these", "those",
    "within", "onto", "over", "under", "unto", "very", "some", "than", "because",
    "daily", "bibletrack", "summary", "reading", "commentary",
}


def iso_lastmod(path: Path) -> str:
    modified = datetime.fromtimestamp(path.stat().st_mtime, tz=timezone.utc)
    return modified.strftime("%Y-%m-%d")


def is_excluded(path: Path) -> bool:
    rel = path.relative_to(ROOT).as_posix()
    return any(part in rel for part in EXCLUDED_PATH_PARTS)


def build_urlset() -> list[tuple[str, str]]:
    entries: list[tuple[str, str]] = []
    root_files = ["index.html", "Search.html"]

    for name in root_files:
        path = ROOT / name
        if path.exists():
            loc = f"{SITE_URL}/{name}" if name != "index.html" else f"{SITE_URL}/"
            entries.append((loc, iso_lastmod(path)))

    for path in sorted((ROOT / "summary2").glob("*/*.html")):
        if path.parent.name not in {"kjv", "nkjv"}:
            continue
        if is_excluded(path):
            continue
        rel = path.relative_to(ROOT).as_posix()
        entries.append((f"{SITE_URL}/{rel}", iso_lastmod(path)))

    for path in sorted((ROOT / "notes" / "resource").glob("*/*.html")):
        if is_excluded(path):
            continue
        rel = path.relative_to(ROOT).as_posix()
        entries.append((f"{SITE_URL}/{rel}", iso_lastmod(path)))

    return entries


def write_robots() -> None:
    content = (
        "User-agent: *\n"
        "Allow: /\n\n"
        f"Sitemap: {SITE_URL}/sitemap.xml\n"
    )
    (ROOT / "robots.txt").write_text(content, encoding="utf-8")


def write_sitemap(entries: list[tuple[str, str]]) -> None:
    lines = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">',
    ]
    for loc, lastmod in entries:
        lines.extend(
            [
                "  <url>",
                f"    <loc>{loc}</loc>",
                f"    <lastmod>{lastmod}</lastmod>",
                "  </url>",
            ]
        )
    lines.append("</urlset>")
    (ROOT / "sitemap.xml").write_text("\n".join(lines) + "\n", encoding="utf-8")


def clean_text(text: str) -> str:
    text = unescape(text)
    text = text.replace("&nbsp;", " ")
    text = re.sub(r"<script\b.*?</script>", " ", text, flags=re.I | re.S)
    text = re.sub(r"<style\b.*?</style>", " ", text, flags=re.I | re.S)
    text = re.sub(r"<[^>]+>", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def tokenize(text: str) -> list[str]:
    words = re.findall(r"[a-z0-9']+", text.lower())
    tokens: list[str] = []
    for word in words:
        word = word.strip("'")
        if len(word) < 3 or word in STOP_WORDS:
            continue
        tokens.append(word)
    return tokens


def collect_search_documents() -> tuple[list[dict], dict[str, list[int]]]:
    docs: list[dict] = []
    inverted: dict[str, list[int]] = {}
    paths = []
    paths.extend(sorted((ROOT / "summary2").glob("*/*.html")))
    paths.extend(sorted((ROOT / "notes" / "resource").glob("*/*.html")))
    paths.append(ROOT / "index.html")

    for path in paths:
        if not path.exists():
            continue
        if path.parent.name not in {"kjv", "nkjv", "easton", "misc"} and path.name != "index.html":
            continue
        if path.name != "index.html" and is_excluded(path):
            continue
        raw = path.read_text(encoding="latin-1", errors="ignore")
        title_match = re.search(r"<title>(.*?)</title>", raw, flags=re.I | re.S)
        title = clean_text(title_match.group(1)) if title_match else path.stem.replace("_", " ")
        text = clean_text(raw)
        if path.name == "index.html":
            url = f"{SITE_URL}/"
            category = "Home"
        else:
            rel = path.relative_to(ROOT).as_posix()
            url = f"{SITE_URL}/{rel}"
            if "summary2/kjv" in rel:
                category = "Daily Summary (KJV)"
            elif "summary2/nkjv" in rel:
                category = "Daily Summary (NKJV)"
            elif "notes/resource/easton" in rel:
                category = "Easton's Resource"
            else:
                category = "Study Resource"

        excerpt = text[:220].rsplit(" ", 1)[0] + "..." if len(text) > 220 else text
        doc_id = len(docs)
        docs.append(
            {
                "id": doc_id,
                "title": title,
                "url": url,
                "category": category,
                "excerpt": excerpt,
            }
        )

        seen = set()
        for token in tokenize(f"{title} {text}"):
            if token in seen:
                continue
            seen.add(token)
            inverted.setdefault(token, []).append(doc_id)

    return docs, inverted


def write_search_index() -> None:
    docs, inverted = collect_search_documents()
    payload = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "documents": docs,
        "index": inverted,
    }
    SEARCH_INDEX_PATH.write_text(json.dumps(payload, separators=(",", ":")), encoding="utf-8")


def main() -> None:
    entries = build_urlset()
    write_robots()
    write_sitemap(entries)
    write_search_index()
    print(f"Wrote robots.txt, sitemap.xml, and search-index.json with {len(entries)} URLs.")


if __name__ == "__main__":
    main()
