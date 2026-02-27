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

This rebuilds changed pages into `upload/summary2/...`.

Example outputs:
- `upload/summary2/kjv/1-1.html`
- `upload/summary2/nkjv/1-1.html`

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
```

Verify after upload:

```text
ls -l /home/waynedturner/public_html/summary2/kjv/1-1.html
ls -l /home/waynedturner/public_html/summary2/nkjv/1-1.html
```

Important: uploading to `/home/waynedturner/summary2/...` fails. Use `/home/waynedturner/public_html/summary2/...`.

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
4. Verify with remote `ls -l`.
5. Hard refresh browser to confirm live output.

