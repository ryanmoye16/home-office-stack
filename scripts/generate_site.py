#!/usr/bin/env python3
"""
generate_site.py — Rebuild homepage picks grid and footer from featured-products.json

Single source of truth: data/featured-products.json
Run this every time the top-6 desk gear list changes.

Usage:
    python3 scripts/generate_site.py
"""

import re
import sys
from pathlib import Path

REPO = Path(__file__).parent.parent
DATA_FILE = REPO / "data" / "featured-products.json"
INDEX_FILE = REPO / "index.html"
AMAZON_TAG = "homeofficestack-20"


def load_products():
    with open(DATA_FILE) as f:
        import json
        return json.load(f)["desk_gear"]


def short_name(product):
    """Generate a concise footer link name from product name."""
    name = product["name"]
    if "USB-C Hub" in name and "Anker" in name:
        return "Anker USB-C Hub"
    if "Smart Plug" in name:
        return "TP-Link Kasa EP25"
    if "Monitor Arm" in name and "Amazon Basics" in name:
        return "Amazon Basics Arm"
    if "Light Bar" in name:
        return "Quntis Monitor Light Bar"
    if "Laptop Stand" in name:
        return "Amazon Basics Laptop Stand"
    if "Desk Mat" in name:
        return "YSAGi Desk Mat"
    return name


def build_picks_grid(products):
    """Build the homepage picks grid HTML.

    Card structure: image full-width at top, content below.
    Single unified card — no side-by-side layout.
    Rank number appears as a small badge overlaid on the image corner.
    """
    lines = []
    for i, p in enumerate(products, start=1):
        num = f"0{i}" if i < 10 else str(i)
        lines.append(f'        <a href="/reviews/{p["slug"]}.html" class="pick-card">')
        lines.append(f'          <div class="pick-card-img-wrap">')
        lines.append(f'            <img src="{p["amazon_image"]}" alt="{p["name"]}" class="pick-card-img" loading="lazy">')
        lines.append(f'            <span class="pick-card-badge">{num}</span>')
        lines.append(f'          </div>')
        lines.append(f'          <div class="pick-card-body">')
        lines.append(f'            <div class="pick-card-header">')
        lines.append(f'              <h3>{p["name"]}</h3>')
        lines.append(f'              <div class="pick-card-meta">')
        lines.append(f'                <span class="pick-card-price">{p["price"]}</span>')
        lines.append(f'                <span class="pick-card-rating">{p["rating_stars"]} {p["rating_value"]}</span>')
        lines.append(f'                <span class="pick-card-reviews">{p["review_count"]} reviews</span>')
        lines.append(f'              </div>')
        lines.append(f'            </div>')
        lines.append(f'            <p class="pick-card-tagline">{p["tagline"]}</p>')
        lines.append(f'            <a href="https://www.amazon.com/dp/{p["asin"]}?tag={AMAZON_TAG}" class="pick-card-btn" target="_blank" rel="nofollow noopener" onclick="event.stopPropagation();">Check Price on Amazon →</a>')
        lines.append(f'          </div>')
        lines.append(f'        </a>')
    return "\n".join(lines)


def build_footer_links(products):
    """Build footer Desk Gear <li> items (6 products + 'All Desk Gear' link)."""
    lines = []
    for p in products:
        lines.append(f'            <li><a href="/reviews/{p["slug"]}.html">{short_name(p)}</a></li>')
    lines.append(f'            <li><a href="/categories/desk-gear.html">All Desk Gear →</a></li>')
    return "\n".join(lines)


def bump_css_version(content):
    """Bump the CSS cache-bust version (?v=N) each time the site is generated."""
    import re
    pattern = re.compile(r'href="css/style\.css\?v=(\d+)"')
    def replacer(m):
        new_version = int(m.group(1)) + 1
        return f'href="css/style.css?v={new_version}"'
    new_content, count = pattern.subn(replacer, content)
    if count == 0:
        # No version param yet — add it
        new_content = re.sub(r'href="css/style\.css"', r'href="css/style.css?v=1"', content)
    return new_content


def replace_picks_grid(content, new_grid):
    """Replace the content between <div class="picks-grid"> and its closing </div>."""
    # Opening: 6 spaces + <div class="picks-grid">
    # Closing: 6 spaces + </div>
    # Content between: any number of spaces
    pattern = re.compile(
        r'(      <div class="picks-grid">)\n(.*?)\n(      </div>)',
        re.DOTALL
    )
    replacement = rf'\1\n{new_grid}\n\3'
    new_content, count = pattern.subn(replacement, content)
    if count == 0:
        print("WARNING: Could not find picks-grid div to replace", file=sys.stderr)
    return new_content


def replace_footer_links(content, new_links):
    """Replace the Desk Gear <ul> contents in the footer."""
    pattern = re.compile(
        r'(<h4>Desk Gear</h4>\s*<ul>)\n(.*?)\n(\s*</ul>\s*\n\s*</div>)',
        re.DOTALL
    )
    replacement = rf'\1\n{new_links}\n\3'
    new_content, count = pattern.subn(replacement, content)
    if count == 0:
        print("WARNING: Could not find footer Desk Gear <ul> to replace", file=sys.stderr)
    return new_content


def main():
    if not DATA_FILE.exists():
        print(f"ERROR: {DATA_FILE} not found", file=sys.stderr)
        sys.exit(1)

    products = load_products()
    print(f"📦 Loaded {len(products)} featured products from {DATA_FILE}")

    new_grid = build_picks_grid(products)
    new_footer = build_footer_links(products)

    content = INDEX_FILE.read_text()
    content = bump_css_version(content)
    content = replace_picks_grid(content, new_grid)
    content = replace_footer_links(content, new_footer)

    INDEX_FILE.write_text(content)
    print(f"✅ Updated {INDEX_FILE}")
    print()
    print("Next steps:")
    print("  1. Review:  git diff index.html")
    print("  2. Commit:  git add index.html && git commit -m 'Update featured products'")
    print("  3. Push:   git push origin main")


if __name__ == "__main__":
    main()
