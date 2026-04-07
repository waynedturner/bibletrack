#!/usr/bin/env python3

import html
import re
from pathlib import Path
from typing import Optional


ROOT = Path("/Users/waynet/Documents/bibletrack_website")
TARGET_DIRS = [
    ROOT / "notes/resource/easton",
    ROOT / "notes/resource/misc",
]

STYLE = """\t\t<style type="text/css">
\t\t\tbody {
\t\t\t\tmargin: 0;
\t\t\t\tpadding: 24px;
\t\t\t\tfont-family: "Helvetica Neue", Helvetica, Arial, sans-serif;
\t\t\t\tcolor: #1f2933;
\t\t\t\tbackground: #f5f1e8;
\t\t\t\tline-height: 1.7;
\t\t\t}
\t\t\ta {
\t\t\t\tcolor: #183153;
\t\t\t}
\t\t\t.page-shell {
\t\t\t\twidth: 960px;
\t\t\t\tmax-width: 100%;
\t\t\t\tmargin: 0 auto;
\t\t\t\tpadding: 26px 30px 36px;
\t\t\t\tborder: 1px solid #d8ccb6;
\t\t\t\tborder-radius: 18px;
\t\t\t\tbox-shadow: 0 18px 45px rgba(15, 35, 64, 0.10);
\t\t\t\tbackground: rgba(255, 255, 255, 0.97);
\t\t\t}
\t\t\t.header-bar {
\t\t\t\tdisplay: flex;
\t\t\t\tjustify-content: space-between;
\t\t\t\talign-items: center;
\t\t\t\tgap: 18px;
\t\t\t\tflex-wrap: wrap;
\t\t\t\tmargin-bottom: 22px;
\t\t\t\tpadding-bottom: 18px;
\t\t\t\tborder-bottom: 1px solid #d8ccb6;
\t\t\t}
\t\t\t.header-logo img {
\t\t\t\tdisplay: block;
\t\t\t\twidth: 260px;
\t\t\t\tmax-width: 100%;
\t\t\t\theight: auto;
\t\t\t}
\t\t\t.header-tools {
\t\t\t\tdisplay: flex;
\t\t\t\talign-items: center;
\t\t\t\tgap: 10px;
\t\t\t\tflex-wrap: wrap;
\t\t\t\tjustify-content: flex-end;
\t\t\t}
\t\t\t.header-button {
\t\t\t\tdisplay: inline-block;
\t\t\t\tpadding: 10px 14px;
\t\t\t\tborder: 1px solid #d8ccb6;
\t\t\t\tborder-radius: 999px;
\t\t\t\tbackground: #ffffff;
\t\t\t\tcolor: #0f2340;
\t\t\t\tfont-size: 14px;
\t\t\t\tfont-weight: bold;
\t\t\t\ttext-decoration: none;
\t\t\t}
\t\t\t.header-button {
\t\t\t\tcursor: pointer;
\t\t\t}
\t\t\t.resource-body {
\t\t\t\tfont-size: 16px;
\t\t\t}
\t\t\t.resource-body p,
\t\t\t.resource-body blockquote,
\t\t\t.resource-body ul,
\t\t\t.resource-body ol,
\t\t\t.resource-body table,
\t\t\t.resource-body div {
\t\t\t\tmax-width: 100%;
\t\t\t}
\t\t\t.resource-body p,
\t\t\t.resource-body blockquote {
\t\t\t\tmargin: 0 0 16px;
\t\t\t}
\t\t\t.resource-body blockquote {
\t\t\t\tmargin-left: 0;
\t\t\t\tpadding: 14px 18px;
\t\t\t\tborder-left: 4px solid #d8ccb6;
\t\t\t\tborder-radius: 12px;
\t\t\t\tbackground: #f7f3ea;
\t\t\t}
\t\t\t.resource-body div[align="center"] {
\t\t\t\ttext-align: center;
\t\t\t\tmargin-bottom: 20px;
\t\t\t\tpadding-bottom: 14px;
\t\t\t\tborder-bottom: 1px solid #e5dccb;
\t\t\t}
\t\t\t.resource-body div[align="left"] {
\t\t\t\ttext-align: left;
\t\t\t}
\t\t\t.resource-body font {
\t\t\t\tfont-family: inherit;
\t\t\t\tcolor: inherit;
\t\t\t}
\t\t\t.resource-body font[size="1"] {
\t\t\t\tfont-size: 13px;
\t\t\t\tcolor: #5d6b79;
\t\t\t\tline-height: 1.5;
\t\t\t}
\t\t\t.resource-body font[size="2"] {
\t\t\t\tfont-size: 16px;
\t\t\t\tcolor: #1f2933;
\t\t\t\tline-height: 1.7;
\t\t\t}
\t\t\t.resource-body font[size="3"] {
\t\t\t\tfont-size: 18px;
\t\t\t\tcolor: #183153;
\t\t\t\tline-height: 1.6;
\t\t\t}
\t\t\t.resource-body font[size="4"] {
\t\t\t\tfont-size: 28px;
\t\t\t\tcolor: #0f2340;
\t\t\t\tline-height: 1.3;
\t\t\t}
\t\t\t.resource-body font[size="5"],
\t\t\t.resource-body font[size="6"] {
\t\t\t\tfont-size: 32px;
\t\t\t\tcolor: #0f2340;
\t\t\t\tline-height: 1.2;
\t\t\t}
\t\t\t.resource-body table {
\t\t\t\twidth: 100%;
\t\t\t\tborder-collapse: collapse;
\t\t\t\tmargin: 18px 0;
\t\t\t\tbackground: #fffdf8;
\t\t\t}
\t\t\t.resource-body td,
\t\t\t.resource-body th {
\t\t\t\tpadding: 10px 12px;
\t\t\t\tborder: 1px solid #d8ccb6;
\t\t\t\tvertical-align: top;
\t\t\t}
\t\t\t.resource-body img {
\t\t\t\tmax-width: 100%;
\t\t\t\theight: auto;
\t\t\t}
\t\t\t@media (max-width: 720px) {
\t\t\t\tbody {
\t\t\t\t\tpadding: 14px;
\t\t\t\t}
\t\t\t\t.page-shell {
\t\t\t\t\tpadding: 18px;
\t\t\t\t}
\t\t\t\t.header-tools {
\t\t\t\t\tjustify-content: flex-start;
\t\t\t\t}
\t\t\t}
\t\t</style>"""


def clean_analytics(text: str) -> str:
    text = re.sub(
        r'\s*<script[^>]*src="http://www\.google-analytics\.com/urchin\.js"[^>]*>\s*</script>\s*'
        r'<script[^>]*>.*?urchinTracker\(\);\s*</script>\s*',
        "\n",
        text,
        flags=re.S,
    )
    return text


def strip_generated_shell(text: str) -> str:
    while '<div class="page-shell">' in text and '<div class="header-bar">' in text:
        match = re.search(
            r'<div class="resource-body">\s*(.*)\s*</div>\s*</div>\s*$',
            text,
            flags=re.S | re.I,
        )
        if not match:
            break
        text = match.group(1).strip()
    return text


def normalize_links_and_copyright(text: str) -> str:
    text = re.sub(r'\s+target="_blank"', "", text, flags=re.I)
    text = re.sub(
        r'Copyright\s+\d{4}(?:-\d{4})?',
        'Copyright 2003-2026',
        text,
        flags=re.I,
    )
    return text


def extract_heading_text(body_html: str) -> Optional[str]:
    match = re.search(
        r'<font size="[3456]">\s*(?:<b>)?(.*?)(?:</b>)?\s*(?:<br\s*/?>)?\s*</font>',
        body_html,
        flags=re.S | re.I,
    )
    if not match:
        return None
    heading = re.sub(r"<[^>]+>", "", match.group(1))
    heading = html.unescape(heading).strip()
    return heading or None


def modernize_document(path: Path) -> None:
    original = path.read_text(encoding="latin-1")
    source_label = (
        "Easton's Bible Dictionary"
        if "easton" in path.parts
        else "BibleTrack Resource"
    )
    title_match = re.search(r"<title>(.*?)</title>", original, flags=re.S | re.I)
    title = title_match.group(1).strip() if title_match else path.stem
    body_match = re.search(r"<body[^>]*>(.*)</body>", original, flags=re.S | re.I)
    if not body_match:
        raise ValueError(f"Could not find body in {path}")

    inner = clean_analytics(body_match.group(1)).strip()
    inner = strip_generated_shell(inner)
    inner = normalize_links_and_copyright(inner)
    heading = extract_heading_text(inner)
    if title.lower().startswith("blank") and heading:
        title = heading

    new_doc = (
        '<!DOCTYPE html PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN">\n\n'
        "<html>\n\n"
        "\t<head>\n"
        '\t\t<meta http-equiv="content-type" content="text/html;charset=ISO-8859-1">\n'
        '\t\t<meta name="generator" content="Adobe GoLive 6">\n'
        f"\t\t<title>{html.escape(title)}</title>\n\n"
        f"{STYLE}\n\n"
        "\t</head>\n\n"
        "\t<body>\n"
        '\t\t<div class="page-shell">\n'
        '\t\t\t<div class="header-bar">\n'
        '\t\t\t\t<a class="header-logo" href="http://www.bibletrack.org/" target="_self"><img src="../../../BT-logo_289x62.jpg" alt="BibleTrack" /></a>\n'
        '\t\t\t\t<div class="header-tools">\n'
        '\t\t\t\t\t<a class="header-button" href="javascript:history.back()">Back</a>\n'
        "\t\t\t\t</div>\n"
        "\t\t\t</div>\n"
        '\t\t\t<div class="resource-body">\n'
        f"{inner}\n"
        "\t\t\t</div>\n"
        "\t\t</div>\n"
        "\t</body>\n\n"
        "</html>\n"
    )
    path.write_text(new_doc, encoding="latin-1")


def main() -> None:
    for directory in TARGET_DIRS:
        for path in sorted(directory.glob("*.html")):
            modernize_document(path)


if __name__ == "__main__":
    main()
