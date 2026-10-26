#!/usr/bin/env python3
"""
update_sitemap_lastmod.py — Stamp <lastmod> on every sitemap URL from git.

For each <loc> in sitemap.xml, the last-modified date is the date of the
most recent git commit that touched the file the URL maps to
(``git log -1 --format=%cs -- <file>``). Files with no git history yet
(new, uncommitted pages) fall back to the file's mtime date.

Run this before every publish that changes any page, so the sitemap
always carries real lastmod dates:

    python3 scripts/update_sitemap_lastmod.py

Idempotent: existing <lastmod> values are replaced in place, all other
sitemap content (changefreq, priority, formatting) is preserved.
"""

import re
import subprocess
import sys
import xml.etree.ElementTree as ET
from datetime import datetime
from pathlib import Path

REPO = Path(__file__).parent.parent
SITEMAP = REPO / "sitemap.xml"


def git_lastmod(relpath):
    try:
        out = subprocess.run(
            ["git", "log", "-1", "--format=%cs", "--", relpath],
            cwd=REPO, capture_output=True, text=True, timeout=15,
        )
        date = out.stdout.strip()
        if re.fullmatch(r"\d{4}-\d{2}-\d{2}", date):
            return date
    except Exception:
        pass
    # Fallback: file mtime (uncommitted / not-yet-tracked page)
    fpath = REPO / relpath
    if fpath.exists():
        return datetime.fromtimestamp(fpath.stat().st_mtime).strftime("%Y-%m-%d")
    return None


def loc_to_relpath(loc):
    # Strip scheme + host, then the leading slash; "" is the homepage.
    path = re.sub(r"^https?://[^/]+", "", loc).lstrip("/")
    return path if path else "index.html"


def main():
    if not SITEMAP.exists():
        print(f"ERROR: {SITEMAP} not found", file=sys.stderr)
        sys.exit(1)

    text = SITEMAP.read_text()
    blocks = list(re.finditer(r"<url>.*?</url>", text, re.DOTALL))
    if not blocks:
        print("ERROR: no <url> blocks found in sitemap", file=sys.stderr)
        sys.exit(1)

    updated = 0
    skipped = []

    def stamp_block(m):
        nonlocal updated
        block = m.group(0)
        loc_m = re.search(r"<loc>([^<]+)</loc>", block)
        if not loc_m:
            return block
        loc = loc_m.group(1)
        date = git_lastmod(loc_to_relpath(loc))
        if not date:
            skipped.append(loc)
            return block
        updated += 1
        if "<lastmod>" in block:
            return re.sub(r"<lastmod>[^<]*</lastmod>", f"<lastmod>{date}</lastmod>", block, count=1)
        # Insert directly after </loc>: keep multi-line sitemaps multi-line.
        after = block[loc_m.end():loc_m.end() + 1]
        if after == "\n":
            return block[:loc_m.end()] + f"\n    <lastmod>{date}</lastmod>" + block[loc_m.end():]
        return block[:loc_m.end()] + f"<lastmod>{date}</lastmod>" + block[loc_m.end():]

    new_text = re.sub(r"<url>.*?</url>", stamp_block, text, flags=re.DOTALL)

    # Validate before writing: must be well-formed XML with the same URL count.
    ET.fromstring(new_text)
    if new_text.count("<loc>") != text.count("<loc>"):
        print("ERROR: URL count changed; not writing", file=sys.stderr)
        sys.exit(1)
    if new_text.count("<lastmod>") != text.count("<loc>"):
        print(f"ERROR: lastmod count != loc count; skipped={skipped}", file=sys.stderr)
        sys.exit(1)

    SITEMAP.write_text(new_text)
    print(f"Stamped <lastmod> on {updated} URLs in sitemap.xml")
    if skipped:
        print(f"WARNING: no date found for: {skipped}", file=sys.stderr)


if __name__ == "__main__":
    main()
