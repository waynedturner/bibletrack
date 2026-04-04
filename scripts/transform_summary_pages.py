from pathlib import Path
import re


STYLE_BLOCK = """
\t\t<style type="text/css">
\t\t\tbody {
\t\t\t\tmargin: 0;
\t\t\t\tpadding: 24px;
\t\t\t\tfont-family: "Helvetica Neue", Helvetica, Arial, sans-serif;
\t\t\t\tcolor: #1f2933;
\t\t\t\tbackground:
\t\t\t\t\tradial-gradient(circle at top right, rgba(239, 230, 211, 0.8), transparent 26%),
\t\t\t\t\tlinear-gradient(180deg, #ffffff 0%, #fffdf8 48%, #ffffff 100%);
\t\t\t\tline-height: 1.6;
\t\t\t}
\t\t\ta {
\t\t\t\tcolor: #183153;
\t\t\t}
\t\t\t.page-shell {
\t\t\t\tmax-width: 1040px;
\t\t\t\tmargin: 0 auto;
\t\t\t\tpadding: 26px 30px 42px;
\t\t\t\tborder: 1px solid #d8ccb6;
\t\t\t\tborder-radius: 18px;
\t\t\t\tbox-shadow: 0 18px 45px rgba(15, 35, 64, 0.10);
\t\t\t\tbackground: rgba(255, 255, 255, 0.96);
\t\t\t}
\t\t\t.header-bar {
\t\t\t\tdisplay: flex;
\t\t\t\tjustify-content: space-between;
\t\t\t\talign-items: center;
\t\t\t\tgap: 18px;
\t\t\t\tflex-wrap: wrap;
\t\t\t\tmargin-bottom: 16px;
\t\t\t\tpadding-bottom: 18px;
\t\t\t\tborder-bottom: 1px solid #d8ccb6;
\t\t\t}
\t\t\t.header-logo img {
\t\t\t\tdisplay: block;
\t\t\t\twidth: 260px;
\t\t\t\tmax-width: 100%;
\t\t\t\theight: auto;
\t\t\t}
\t\t\t.header-controls {
\t\t\t\tdisplay: flex;
\t\t\t\tflex-direction: column;
\t\t\t\talign-items: flex-end;
\t\t\t\tgap: 12px;
\t\t\t}
\t\t\t.header-links,
\t\t\t.version-toggle,
\t\t\t.header-tools {
\t\t\t\tdisplay: flex;
\t\t\t\tflex-wrap: wrap;
\t\t\t\tgap: 10px;
\t\t\t\tjustify-content: flex-end;
\t\t\t}
\t\t\t.header-button,
\t\t\t.toggle-button {
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
\t\t\t.toggle-button.active {
\t\t\t\tbackground: #183153;
\t\t\t\tborder-color: #183153;
\t\t\t\tcolor: #ffffff;
\t\t\t}
\t\t\t.article-card {
\t\t\t\tmargin: 18px 0 20px;
\t\t\t\tpadding: 18px 20px;
\t\t\t\tborder: 1px solid #d8ccb6;
\t\t\t\tborder-radius: 16px;
\t\t\t\tbackground: linear-gradient(180deg, #fbf8f0 0%, #ffffff 100%);
\t\t\t}
\t\t\t.article-card h3 {
\t\t\t\tmargin: 0 0 8px;
\t\t\t\tcolor: #0f2340;
\t\t\t\tfont-size: 18px;
\t\t\t}
\t\t\t.article-card p {
\t\t\t\tmargin: 0;
\t\t\t}
\t\t\t.note-box {
\t\t\t\tfloat: right;
\t\t\t\twidth: 300px;
\t\t\t\tmargin: 6px 0 16px 18px;
\t\t\t\tborder: 1px solid #d8ccb6;
\t\t\t\tborder-radius: 14px;
\t\t\t\tbackground: #f7f3ea;
\t\t\t}
\t\t\t.note-box td {
\t\t\t\tpadding: 12px 14px;
\t\t\t\tcolor: #5d6b79;
\t\t\t}
\t\t\t.page-footer {
\t\t\t\tmargin-top: 28px;
\t\t\t\tpadding-top: 18px;
\t\t\t\tborder-top: 1px solid #d8ccb6;
\t\t\t\tcolor: #5d6b79;
\t\t\t\tfont-size: 12px;
\t\t\t\ttext-align: center;
\t\t\t}
\t\t\t.date-picker {
\t\t\t\tdisplay: flex;
\t\t\t\talign-items: center;
\t\t\t\tflex-wrap: wrap;
\t\t\t\tgap: 8px;
\t\t\t}
\t\t\t.date-picker label {
\t\t\t\tfont-size: 14px;
\t\t\t\tfont-weight: bold;
\t\t\t\tcolor: #5d6b79;
\t\t\t}
\t\t\t.date-picker input {
\t\t\t\tpadding: 9px 12px;
\t\t\t\tborder: 1px solid #d8ccb6;
\t\t\t\tborder-radius: 999px;
\t\t\t\tfont-family: inherit;
\t\t\t\tfont-size: 14px;
\t\t\t}
\t\t\t.date-picker button {
\t\t\t\tpadding: 10px 14px;
\t\t\t\tborder: 1px solid #183153;
\t\t\t\tborder-radius: 999px;
\t\t\t\tbackground: #183153;
\t\t\t\tcolor: #ffffff;
\t\t\t\tfont-family: inherit;
\t\t\t\tfont-size: 14px;
\t\t\t\tfont-weight: bold;
\t\t\t\tcursor: pointer;
\t\t\t}
\t\t\t@media (max-width: 720px) {
\t\t\t\tbody {
\t\t\t\t\tpadding: 14px;
\t\t\t\t}
\t\t\t\t.page-shell {
\t\t\t\t\tpadding: 18px;
\t\t\t\t}
\t\t\t\t.header-controls {
\t\t\t\t\talign-items: flex-start;
\t\t\t\t}
\t\t\t\t.header-links,
\t\t\t\t.version-toggle,
\t\t\t\t.header-tools {
\t\t\t\t\tjustify-content: flex-start;
\t\t\t\t}
\t\t\t\t.note-box {
\t\t\t\t\tfloat: none;
\t\t\t\t\twidth: 100%;
\t\t\t\t\tmargin-left: 0;
\t\t\t\t}
\t\t\t}
\t\t</style>
"""


FOOTER_AND_SCRIPT = """
\t\t<p class="page-footer">Copyright 2003-2026 BibleTrack</p>
\t\t</div>
\t\t<script type="text/javascript">
\t\t\tfunction openSelectedDate(version) {
\t\t\t\tvar input = document.getElementById('reading-date');
\t\t\t\tif (!input || !input.value) {
\t\t\t\t\treturn;
\t\t\t\t}
\t\t\t\tvar parts = input.value.split('-');
\t\t\t\tif (parts.length !== 3) {
\t\t\t\t\treturn;
\t\t\t\t}
\t\t\t\twindow.location.href = parts[1].replace(/^0/, '') + '-' + parts[2].replace(/^0/, '') + '.html';
\t\t\t}
\t\t</script>
\t</body>
"""


BODY_END_RE = re.compile(r"</body>\s*</html>\s*$", re.I | re.S)

def clean_text(text: str) -> str:
    text = re.sub(r"<[^>]+>", " ", text)
    text = text.replace("&nbsp;", " ")
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def html_escape(text: str) -> str:
    return (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def humanize_src(src: str) -> str:
    src = src.split("?")[0]
    name = Path(src).stem
    name = name.replace(";", " ")
    name = name.replace("_", " ")
    name = re.sub(r"(?<=\d)(?=[A-Za-z])", " ", name)
    name = re.sub(r"(?<=[a-z])(?=[A-Z])", " ", name)
    return clean_text(name) or "related resource"


def find_prev_next(text: str):
    nav_match = re.search(
        r"<table[^>]*width=\"?200\"?[^>]*>.*?</table>",
        text,
        re.I | re.S,
    )
    prev_href = prev_label = next_href = next_label = ""
    if nav_match:
        anchors = re.findall(r"<a href=\"([^\"]+)\"[^>]*>(.*?)</a>", nav_match.group(0), re.I | re.S)
        if len(anchors) >= 3:
            prev_href, prev_label = anchors[1]
            next_href, next_label = anchors[2]
    return nav_match.group(0) if nav_match else "", prev_href, clean_text(prev_label), next_href, clean_text(next_label)


def build_header(version: str, slug: str, date_value: str, prev_href: str, prev_label: str, next_href: str, next_label: str) -> str:
    prev_label = prev_label or "Previous"
    next_label = next_label or "Next"
    prev_link = f'\t\t\t\t\t<a class="header-button" href="{prev_href}" target="_self">{html_escape(prev_label)}</a>\n' if prev_href else ""
    next_link = f'\t\t\t\t\t<a class="header-button" href="{next_href}" target="_self">{html_escape(next_label)}</a>\n' if next_href else ""
    if version == "kjv":
        toggle = (
            '\t\t\t\t<div class="version-toggle">\n'
            '\t\t\t\t\t<span class="toggle-button active">KJV</span>\n'
            f'\t\t\t\t\t<a class="toggle-button" href="../nkjv/{slug}" target="_self">NKJV</a>\n'
            '\t\t\t\t</div>\n'
        )
    else:
        toggle = (
            '\t\t\t\t<div class="version-toggle">\n'
            f'\t\t\t\t\t<a class="toggle-button" href="../kjv/{slug}" target="_self">KJV</a>\n'
            '\t\t\t\t\t<span class="toggle-button active">NKJV</span>\n'
            '\t\t\t\t</div>\n'
        )
    return (
        '\t<body>\n'
        '\t\t<div class="page-shell">\n'
        '\t\t<div class="header-bar">\n'
        '\t\t\t<a class="header-logo" href="http://www.bibletrack.org/" target="_self"><img src="../../BT-logo_289x62.jpg" alt="BibleTrack" /></a>\n'
        '\t\t\t<div class="header-controls">\n'
        '\t\t\t\t<div class="header-links">\n'
        '\t\t\t\t\t<a class="header-button" href="http://www.bibletrack.org/" target="_self">Home &amp; Index</a>\n'
        f"{prev_link}"
        f"{next_link}"
        '\t\t\t\t</div>\n'
        f"{toggle}"
        '\t\t\t\t<div class="header-tools">\n'
        '\t\t\t\t\t<div class="date-picker">\n'
        '\t\t\t\t\t\t<label for="reading-date">Select date</label>\n'
        f'\t\t\t\t\t\t<input id="reading-date" type="date" value="{date_value}" />\n'
        f'\t\t\t\t\t\t<button type="button" onclick="openSelectedDate(\'{version}\')">Go</button>\n'
        '\t\t\t\t\t</div>\n'
        '\t\t\t\t</div>\n'
        '\t\t\t</div>\n'
        '\t\t</div>\n'
    )


def build_article_card(src: str) -> str:
    title = humanize_src(src)
    return (
        '\n\t\t<div class="article-card">\n'
        '\t\t\t<h3>Related Article</h3>\n'
        f'\t\t\t<p><a href="{src}" target="_blank">Open the related article on {html_escape(title)}.</a></p>\n'
        '\t\t</div>\n'
    )


def replace_iframe_table(match: re.Match) -> str:
    block = match.group(0)
    src_match = re.search(r'src=\"([^\"]+)\"|SRC=\"([^\"]+)\"', block, re.I)
    if not src_match:
        return ""
    src = src_match.group(1) or src_match.group(2)
    lowered = src.lower()
    if "youtube.com/embed" in lowered or "facebook.com/plugins/like.php" in lowered:
        return "\n"
    return build_article_card(src)


def transform_file(path: Path) -> bool:
    text = path.read_text(encoding="latin-1")
    slug = path.name
    version = path.parent.name
    month, day = path.stem.split("-")
    date_value = f"2026-{int(month):02d}-{int(day):02d}"

    nav_block, prev_href, prev_label, next_href, next_label = find_prev_next(text)

    analytics_match = re.search(
        r'<script[^>]*urchin\.js[^>]*>.*?</script>\s*<script[^>]*>.*?_uacct\s*=.*?urchinTracker\(\);.*?</script>',
        text,
        re.I | re.S,
    )
    analytics = analytics_match.group(0).strip() + "\n" if analytics_match else ""
    if analytics_match:
        text = text.replace(analytics_match.group(0), "")

    text = re.sub(r"</head>", STYLE_BLOCK + "\n\t</head>", text, count=1, flags=re.I)

    body_match = re.search(r"<body[^>]*>(.*)</body>", text, re.I | re.S)
    if not body_match:
        return False

    inner = body_match.group(1)
    if nav_block:
        inner = inner.replace(nav_block, "", 1)

    inner = re.sub(
        r'<p[^>]*>\s*<a href="http://www\.bibletrack\.org/"[^>]*><img[^>]*bible_track_logo[^>]*></a>\s*</p>',
        "",
        inner,
        flags=re.I | re.S,
    )
    inner = re.sub(
        r'<p[^>]*>\s*<a href="\.\./nkjv/[^"]+"[^>]*>.*?For New King James text and comment, click here\..*?</p>',
        "",
        inner,
        flags=re.I | re.S,
    )
    inner = re.sub(
        r'<a href="\.\./(?:nkjv|kjv)/[^"]+"[^>]*>\s*<strong><font[^>]*>For (?:New )?King James text and commentary, click here\.\s*</font></strong></a>',
        "",
        inner,
        flags=re.I | re.S,
    )
    inner = re.sub(
        r'<table[^>]*width="100%"[^>]*>.*?This is the New King James text of the passages\..*?</table>',
        "",
        inner,
        flags=re.I | re.S,
    )
    inner = re.sub(
        r'<table[^>]*width="?244"?[^>]*>.*?youtube\.com/embed.*?</table>',
        "",
        inner,
        flags=re.I | re.S,
    )
    inner = re.sub(
        r'<table[^>]*>\s*<tr>\s*<td[^>]*>\s*(?:<iframe|<IFRAME).*?(?:</iframe>|</IFRAME>)\s*</td>\s*</tr>\s*</table>',
        replace_iframe_table,
        inner,
        flags=re.I | re.S,
    )
    inner = re.sub(
        r'(?:<iframe|<IFRAME).*?(?:</iframe>|</IFRAME>)',
        lambda m: replace_iframe_table(m),
        inner,
        flags=re.I | re.S,
    )
    inner = re.sub(
        r'<img[^>]*src="http://www\.bibletrack\.org/notes/image/audio\.jpg"[^>]*>',
        '<img src="../../listen_icon.svg" alt="Listen" width="40" height="40" border="0" />',
        inner,
        flags=re.I,
    )
    inner = re.sub(
        r'<table([^>]*)bgcolor="#ffea89"([^>]*)>',
        lambda m: f'<table class="note-box"{m.group(1)}{m.group(2)}>',
        inner,
        flags=re.I,
    )
    inner = re.sub(r'\s+bgcolor="#ffea89"', "", inner, flags=re.I)

    header = build_header(version, slug, date_value, prev_href, prev_label, next_href, next_label)
    new_body = header
    if analytics:
        new_body += "\t\t" + analytics.replace("\n", "\n\t\t").rstrip() + "\n"
    new_body += inner.strip() + "\n" + FOOTER_AND_SCRIPT

    text = re.sub(r"<body[^>]*>.*</body>", new_body, text, count=1, flags=re.I | re.S)
    text = BODY_END_RE.sub("</body>\n\n</html>\n", text)
    path.write_text(text, encoding="latin-1")
    return True


def main():
    changed = 0
    for path in sorted(Path("summary2").glob("*/*.html")):
        if path.parent.name not in {"kjv", "nkjv"}:
            continue
        if transform_file(path):
            changed += 1
    print(f"Transformed {changed} files.")


if __name__ == "__main__":
    main()
