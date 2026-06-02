import re
import json
from pathlib import Path
from bs4 import BeautifulSoup, NavigableString, Tag

def normalize_whitespace(text: str) -> str:
    text = text.replace("\xa0", " ")
    text = re.sub(r"[\t\r ]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return "\n".join(line.strip() for line in text.splitlines()).strip()

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
        or stripped.lower().startswith(("kjv", "nkjv", "niv", "esv", "nasb", "nlt"))
    )

def _next_heading(node: Tag) -> Tag | None:
    pointer = node.next_sibling
    while pointer is not None:
        if isinstance(pointer, Tag) and _is_heading(pointer):
            return pointer
        pointer = pointer.next_sibling
    return None

def _collect_text(nodes) -> str:
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

import hashlib
from models import TopicDocument

def parse_topic_file(file_path: Path) -> TopicDocument:
    html = file_path.read_text(encoding="iso-8859-1")
    soup = BeautifulSoup(html, "html.parser")
    
    body = soup.find(class_="resource-body") or soup.body
    headings = [node for node in body.find_all(["h1", "h2", "h3", "h4", "p"]) if _is_heading(node)]
    
    article_text_blocks = []
    
    # Collect text before first heading
    pre_nodes = []
    curr = body.contents[0] if body.contents else None
    while curr and (not headings or curr != headings[0]):
        pre_nodes.append(curr)
        curr = curr.next_sibling
    
    pre_content = _collect_text(pre_nodes)
    if pre_content:
        article_text_blocks.append(pre_content)

    for heading in headings:
        title = normalize_whitespace(heading.get_text(" ", strip=True))
        article_text_blocks.append(f"### {title}")
        
        end_heading = _next_heading(heading)
        nodes = []
        curr = heading.next_sibling
        while curr and curr != end_heading:
            nodes.append(curr)
            curr = curr.next_sibling
        
        content = _collect_text(nodes)
        if content:
            article_text_blocks.append(content)
                
    text = "\n\n".join(article_text_blocks)
    content_hash = hashlib.sha256(text.encode("utf-8")).hexdigest()
    slug = file_path.stem.lower().replace("_", "-")
    
    return TopicDocument(
        id=f"bibletrack:topic:{slug}",
        title=soup.find("title").get_text(strip=True) if soup.find("title") else file_path.stem,
        content=text,
        source_url=f"https://www.bibletrack.org/notes/resource/misc/{file_path.name}",
        content_hash=content_hash,
        slug=slug
    )
