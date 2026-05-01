from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path
from typing import Iterable
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup, NavigableString, Tag

from models import DayDocument, Section, SourceLink

BASE_URL = "https://www.bibletrack.org/summary2/{translation}/{date_key}.html"

BOOK_NAMES = (
    "Genesis|Exodus|Leviticus|Numbers|Deuteronomy|Joshua|Judges|Ruth|"
    "1\\sSamuel|2\\sSamuel|1\\sKings|2\\sKings|1\\sChronicles|2\\sChronicles|"
    "Ezra|Nehemiah|Esther|Job|Psalms?|Proverbs|Ecclesiastes|Song\\sof\\sSolomon|"
    "Isaiah|Jeremiah|Lamentations|Ezekiel|Daniel|Hosea|Joel|Amos|Obadiah|Jonah|"
    "Micah|Nahum|Habakkuk|Zephaniah|Haggai|Zechariah|Malachi|Matthew|Mark|Luke|John|"
    "Acts|Romans|1\\sCorinthians|2\\sCorinthians|Galatians|Ephesians|Philippians|"
    "Colossians|1\\sThessalonians|2\\sThessalonians|1\\sTimothy|2\\sTimothy|Titus|"
    "Philemon|Hebrews|James|1\\sPeter|2\\sPeter|1\\sJohn|2\\sJohn|3\\sJohn|Jude|Revelation"
)
REF_RE = re.compile(rf"\b(?:{BOOK_NAMES})\s+\d+:\d+(?:-\d+)?(?:\s*,\s*\d+:\d+(?:-\d+)?)*")


def get_url(date_key: str, translation: str) -> str:
    return BASE_URL.format(translation=translation.strip().lower(), date_key=date_key.strip())


def fetch_html(url: str) -> str:
    # Try local file first
    parts = url.split("/")
    translation = parts[-2]
    date_key = parts[-1].replace(".html", "")
    local_path = Path(f"summary2/{translation}/{date_key}.html")

    if local_path.exists():
        return local_path.read_text(encoding="iso-8859-1")

    response = requests.get(url, timeout=30)
    response.raise_for_status()
    return response.text


def normalize_whitespace(text: str) -> str:
    text = text.replace("\xa0", " ")
    text = re.sub(r"[\t\r ]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return "\n".join(line.strip() for line in text.splitlines()).strip()


def extract_refs(text: str) -> list[str]:
    refs = [normalize_whitespace(m) for m in REF_RE.findall(text)]
    return sorted(set(refs))


def _classify_link(url: str, link_text: str) -> str:
    signature = f"{url} {link_text}".lower()
    if any(token in signature for token in ("audio", ".mp3", "listen")):
        return "audio"
    if "note" in signature:
        return "note"
    if "bibletrack" in signature:
        return "related"
    return "external"


def _slugify(value: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    return slug or "untitled"


def _is_heading(tag: Tag) -> bool:
    if tag.name in {"h1", "h2", "h3", "h4"}:
        return True
    if tag.name == "p":
        classes = " ".join(tag.get("class", []))
        bold = tag.find(["strong", "b"])
        return "heading" in classes.lower() or (bold is not None and len(tag.get_text(strip=True)) < 120)
    return False


def _is_verse_like_line(line: str) -> bool:
    stripped = line.strip()
    return bool(
        not stripped
        or stripped.startswith(">")
        or re.match(r"^\d{1,3}\s+\S+", stripped)
        or stripped.lower().startswith(("kjv", "nkjv", "niv", "esv", "nasb", "nlt"))
    )


def _next_heading(node: Tag) -> Tag | None:
    pointer = node.next_sibling
    while pointer is not None:
        if isinstance(pointer, Tag) and _is_heading(pointer):
            return pointer
        pointer = pointer.next_sibling
    return None


def _nodes_between(start: Tag, end: Tag | None) -> Iterable[Tag | NavigableString]:
    pointer = start.next_sibling
    while pointer is not None and pointer is not end:
        yield pointer
        pointer = pointer.next_sibling


def _collect_commentary_text(nodes: Iterable[Tag | NavigableString]) -> str:
    chunks: list[str] = []
    for node in nodes:
        if isinstance(node, NavigableString):
            text = normalize_whitespace(str(node))
            if text:
                chunks.append(text)
            continue

        if node.name in {"script", "style", "blockquote"}:
            continue

        text = normalize_whitespace(node.get_text("\n", strip=True))
        if not text:
            continue

        filtered = [line for line in text.splitlines() if not _is_verse_like_line(line)]
        cleaned = normalize_whitespace("\n".join(filtered))
        if cleaned:
            chunks.append(cleaned)

    return normalize_whitespace("\n\n".join(chunks))


def _links_from_node(node: Tag, base_url: str) -> list[SourceLink]:
    links: list[SourceLink] = []
    for anchor in node.find_all("a", href=True):
        absolute = urljoin(base_url, anchor["href"].strip())
        if not absolute.lower().startswith(("http://", "https://")):
            continue
        text = normalize_whitespace(anchor.get_text(" ", strip=True)) or absolute
        links.append(SourceLink(url=absolute, link_text=text, link_type=_classify_link(absolute, text)))
    return links


def _dedupe_links(links: list[SourceLink]) -> list[SourceLink]:
    dedupe: dict[tuple[str, str, str], SourceLink] = {}
    for link in links:
        dedupe[(link.url, link.link_text, link.link_type)] = link
    return [dedupe[key] for key in sorted(dedupe.keys())]


def parse_day(date_key: str, translation: str) -> DayDocument:
    source_url = get_url(date_key, translation)
    html = fetch_html(source_url)
    soup = BeautifulSoup(html, "html.parser")

    headings = [node for node in soup.find_all(["h1", "h2", "h3", "h4", "p"]) if _is_heading(node)]

    all_links: list[SourceLink] = [SourceLink(url=source_url, link_text="source", link_type="source")]
    sections: list[Section] = []

    for heading in headings:
        title = normalize_whitespace(heading.get_text(" ", strip=True))
        if not title:
            continue

        end_heading = _next_heading(heading)
        span_nodes = list(_nodes_between(heading, end_heading))
        commentary = _collect_commentary_text(span_nodes)
        if not commentary:
            continue

        section_links: list[SourceLink] = []
        for node in span_nodes:
            if isinstance(node, Tag):
                section_links.extend(_links_from_node(node, source_url))
        section_links = _dedupe_links(section_links)
        all_links.extend(section_links)

        # Translation-agnostic ID format: bibletrack:{date_key}:{slug}
        section = Section(
            canonical_id=f"bibletrack:{date_key}:{_slugify(title)}",
            title=title,
            commentary_text=commentary,
            bible_references=extract_refs(f"{title}\n{commentary}"),
            links=section_links,
        )
        sections.append(section)

    sections_by_id = {section.canonical_id: section for section in sections}
    ordered_sections = [sections_by_id[key] for key in sorted(sections_by_id.keys())]

    title_blob = "\n".join(
        normalize_whitespace(node.get_text(" ", strip=True)) for node in soup.find_all(["title", "h1", "h2"])
    )
    reading_refs = extract_refs(title_blob)
    all_links = _dedupe_links(all_links)

    hash_payload = {
        "source_url": source_url,
        "translation": translation.lower(),
        "date_key": date_key,
        "reading_refs": reading_refs,
        "sections": [
            {
                "title": section.title,
                "commentary_text": section.commentary_text,
                "links": [link.model_dump() for link in section.links],
            }
            for section in ordered_sections
        ],
        "links": [link.model_dump() for link in all_links],
    }
    content_hash = hashlib.sha256(json.dumps(hash_payload, sort_keys=True, ensure_ascii=False).encode("utf-8")).hexdigest()

    return DayDocument(
        source_url=source_url,
        translation=translation.lower(),
        reading_plan_key=date_key,
        semantic_date=None,
        reading_refs=reading_refs,
        links=all_links,
        sections=ordered_sections,
        content_hash=content_hash,
    )
