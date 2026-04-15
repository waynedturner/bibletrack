# BibleTrack Site Update Runbook

This file documents the working process for editing, generating, and publishing this site.

## 1) Edit content (source of truth)

- KJV pages live in `summary2/kjv/`
- NKJV pages live in `summary2/nkjv/`
- Example for Jan 1:
  - `summary2/kjv/1-1.html`
  - `summary2/nkjv/1-1.html`

Always edit files in `summary2/...`, not in `upload/...`.

## 2) Regenerate upload-ready files

Run:

```bash
./summary_template.sh
```

This rebuilds changed pages into `upload/summary2/...` and also refreshes/stages the search-facing root files into `upload/root/...`.

Example outputs:
- `upload/summary2/kjv/1-1.html`
- `upload/summary2/nkjv/1-1.html`
- `upload/root/index.html`
- `upload/root/Search.html`
- `upload/root/robots.txt`
- `upload/root/sitemap.xml`
- `upload/root/search-index.json`

## 3) Publish to server via SFTP

Connection parameters:
- Protocol: `SFTP`
- Host: `ftp.bibletrack.org`
- Username: `waynedturner`
- Remote web root: `/home/waynedturner/public_html`

Upload commands (inside `sftp`):

```text
put upload/summary2/kjv/1-1.html /home/waynedturner/public_html/summary2/kjv/1-1.html
put upload/summary2/nkjv/1-1.html /home/waynedturner/public_html/summary2/nkjv/1-1.html
put upload/root/index.html /home/waynedturner/public_html/index.html
put upload/root/Search.html /home/waynedturner/public_html/Search.html
put upload/root/robots.txt /home/waynedturner/public_html/robots.txt
put upload/root/sitemap.xml /home/waynedturner/public_html/sitemap.xml
put upload/root/search-index.json /home/waynedturner/public_html/search-index.json
```

Verify after upload:

```text
ls -l /home/waynedturner/public_html/summary2/kjv/1-1.html
ls -l /home/waynedturner/public_html/summary2/nkjv/1-1.html
ls -l /home/waynedturner/public_html/index.html
ls -l /home/waynedturner/public_html/Search.html
ls -l /home/waynedturner/public_html/robots.txt
ls -l /home/waynedturner/public_html/sitemap.xml
ls -l /home/waynedturner/public_html/search-index.json
```

Important: uploading to `/home/waynedturner/summary2/...` fails. Use `/home/waynedturner/public_html/summary2/...`.

### One-command deploy helper

After running `./summary_template.sh`, you can publish the staged files with:

```bash
./deploy_site.sh
```

This uploads:
- `upload/summary2/kjv`
- `upload/summary2/nkjv`
- `upload/root/index.html`
- `upload/root/Search.html`
- `upload/root/robots.txt`
- `upload/root/sitemap.xml`
- `upload/root/search-index.json`

It also verifies the main live files with remote `ls -l` before exiting.

## 4) Git workflow used in this repo

- Ignore local/editor artifacts:
  - `.idea/`
  - `.DS_Store`
  - `upload`
- Branch naming convention used here: `codex/<name>`
- Current remote in use: `origin` -> `git@github.com:waynedturner/bibletrack.git`

Typical flow:

```bash
git checkout -b codex/<topic>
git add -A
git commit -m "Your message"
git push -u origin codex/<topic>
```

## 5) Formatting caution (Jan 1 pages)

When editing the Mark/Luke intro section, keep bold tags tightly scoped.

- Prefer separate heading paragraph + body paragraph, e.g.:
  - `<p><font size="4"><b>The Gospel of Mark</b></font></p>`
  - `<p>Body text...</p>`

This prevents "bold bleed" caused by malformed or ambiguously nested inline tags.

## 6) Quick checklist for any page update

1. Edit `summary2/kjv/<m-d>.html` and/or `summary2/nkjv/<m-d>.html`.
2. Run `./summary_template.sh`.
3. Upload `upload/summary2/...` files to `/home/waynedturner/public_html/summary2/...`.
4. Upload `upload/root/index.html`, `Search.html`, `robots.txt`, `sitemap.xml`, and `search-index.json` when the homepage or search/indexing assets changed.
5. Verify with remote `ls -l`.
6. Hard refresh browser to confirm live output.
