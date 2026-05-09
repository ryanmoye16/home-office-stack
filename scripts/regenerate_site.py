#!/usr/bin/env python3
"""
regenerate_site.py — Regenerate ALL site pages that reference featured products.

Single source of truth: data/featured-products.json
Run this EVERY TIME a product is added, removed, or updated in featured-products.json.

What it updates:
  1. index.html          — homepage picks grid + footer links
  2. categories/*.html    — category page product grids (filtered by category)
  3. categories/desk-gear.html — all-products grid

Usage:
    python3 scripts/regenerate_site.py
"""

import json
import re
import sys
from pathlib import Path

REPO = Path(__file__).parent.parent
DATA_FILE = REPO / "data" / "featured-products.json"
INDEX_FILE = REPO / "index.html"
CATEGORIES_DIR = REPO / "categories"
AMAZON_TAG = "homeofficestack-20"

# ---------------------------------------------------------------------------
# Data loading
# ---------------------------------------------------------------------------

def load_products():
    with open(DATA_FILE) as f:
        return json.load(f)["desk_gear"]


def products_by_category(products, category_slug):
    return [p for p in products if p["category"] == category_slug]


# ---------------------------------------------------------------------------
# HTML builders
# ---------------------------------------------------------------------------

def build_picks_grid(products):
    """Homepage picks grid — all products in order."""
    lines = []
    for i, p in enumerate(products, start=1):
        num = f"0{i}" if i < 10 else str(i)
        lines.append(f'        <a href="/reviews/{p["slug"]}.html" class="pick-card">')
        lines.append(f'          <div class="pick-card-img-wrap">')
        lines.append(f'            <img src="{p["amazon_image"]}" alt="{p["name"]}" class="pick-card-img" loading="lazy">')
        lines.append(f'            <span class="pick-card-badge">{num}</span>')
        lines.append(f'          </div>')
        lines.append(f'          <div class="pick-card-body">')
        lines.append(f'            <h3>{p["name"]}</h3>')
        lines.append(f'            <div class="pick-card-meta">')
        lines.append(f'              <span class="pick-card-price">{p["price"]}</span>')
        lines.append(f'              <span class="pick-card-rating">{p["rating_stars"]} {p["rating_value"]}</span>')
        lines.append(f'              <span class="pick-card-reviews">{p["review_count"]} reviews</span>')
        lines.append(f'            </div>')
        lines.append(f'            <p class="pick-card-tagline">{p["tagline"]}</p>')
        lines.append(f'            <div class="pick-card-btn" onclick="window.open(\'https://www.amazon.com/dp/{p["asin"]}?tag={AMAZON_TAG}\', \'_blank\', \'noopener,nofollow\');">Check Price on Amazon →</div>')
        lines.append(f'          </div>')
        lines.append(f'        </a>')
    return "\n".join(lines)


def build_category_grid(products):
    """Category page grid — filtered to one category."""
    lines = []
    for i, p in enumerate(products, start=1):
        num = f"0{i}" if i < 10 else str(i)
        lines.append(f'        <a href="../reviews/{p["slug"]}.html" class="pick-card">')
        lines.append(f'          <div class="pick-card-img-wrap">')
        lines.append(f'            <img src="{p["amazon_image"]}" alt="{p["name"]}" class="pick-card-img" loading="lazy">')
        lines.append(f'            <span class="pick-card-badge">{num}</span>')
        lines.append(f'          </div>')
        lines.append(f'          <div class="pick-card-body">')
        lines.append(f'            <h3>{p["name"]}</h3>')
        lines.append(f'            <div class="pick-card-meta">')
        lines.append(f'              <span class="pick-card-price">{p["price"]}</span>')
        lines.append(f'              <span class="pick-card-rating">{p["rating_stars"]} {p["rating_value"]}</span>')
        lines.append(f'              <span class="pick-card-reviews">{p["review_count"]} reviews</span>')
        lines.append(f'            </div>')
        lines.append(f'            <p class="pick-card-tagline">{p["tagline"]}</p>')
        lines.append(f'            <div class="pick-card-btn" onclick="window.open(\'https://www.amazon.com/dp/{p["asin"]}?tag={AMAZON_TAG}\', \'_blank\', \'noopener,nofollow\');">Check Price on Amazon →</div>')
        lines.append(f'          </div>')
        lines.append(f'        </a>')
    return "\n".join(lines)


def short_name(product):
    """Concise footer link name."""
    name = product["name"]
    if "Anker 7-in-1" in name or "Anker" in name and "Hub" in name:
        return "Anker USB-C Hub"
    if "Kasa EP25" in name or "Smart Plug" in name and "Kasa" in name:
        return "TP-Link Kasa EP25"
    if "Monitor Arm" in name and "Amazon Basics" in name:
        return "Amazon Basics Arm"
    if "Quntis" in name or "Monitor Light Bar" in name:
        return "Quntis Monitor Light Bar"
    if "Rain Design" in name or "iLevel" in name:
        return "Rain Design iLevel 2"
    if "Upryze" in name or "Lifelong" in name:
        return "Lifelong Upryze"
    if "Laptop Stand" in name and "Amazon Basics" in name:
        return "Amazon Basics Laptop Stand"
    if "YSAGi" in name or "Desk Mat" in name:
        return "YSAGi Desk Mat"
    if "Amazon Smart Plug" in name:
        return "Amazon Smart Plug"
    if "North Bayou" in name or "F80" in name:
        return "North Bayou F80"
    if "Anker 555" in name or "8-in-1" in name:
        return "Anker 555 USB-C Hub"
    if "Ergodriven" in name or "Topo" in name:
        return "Ergodriven Topo Mini"
    return name


def build_footer_links(products):
    """Footer Desk Gear <li> items."""
    lines = []
    for p in products:
        lines.append(f'            <li><a href="/reviews/{p["slug"]}.html">{short_name(p)}</a></li>')
    lines.append(f'            <li><a href="/categories/desk-gear.html">All Desk Gear →</a></li>')
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Replacement helpers
# ---------------------------------------------------------------------------

def bump_css_version(content):
    pattern = re.compile(r'href="css/style\.css\?v=(\d+)"')
    def replacer(m):
        new_version = int(m.group(1)) + 1
        return f'href="css/style.css?v={new_version}"'
    new_content, count = pattern.subn(replacer, content)
    if count == 0:
        new_content = re.sub(r'href="css/style\.css"', r'href="css/style.css?v=1"', content)
    return new_content


def replace_picks_grid(content, new_grid):
    """Replace content between <div class="picks-grid"> and its closing </div>."""
    # Category pages: 4 spaces indent (inside main content wrapper)
    # Homepage: 6 spaces indent
    pattern_6 = re.compile(
        r'(      <div class="picks-grid">)\n(.*?)\n(      </div>)',
        re.DOTALL
    )
    pattern_4 = re.compile(
        r'(    <div class="picks-grid">)\n(.*?)\n(    </div>)',
        re.DOTALL
    )
    for pattern in [pattern_6, pattern_4]:
        new_content, count = pattern.subn(r'\1\n' + new_grid + r'\n\3', content)
        if count > 0:
            return new_content
    print("  WARNING: Could not find picks-grid div to replace", file=sys.stderr)
    return content


def replace_footer_links(content, new_links):
    pattern = re.compile(
        r'(<h4>Desk Gear</h4>\s*<ul>)\n(.*?)\n(\s*</ul>\s*\n\s*</div>)',
        re.DOTALL
    )
    replacement = r'\1\n' + new_links + r'\n\3'
    new_content, count = pattern.subn(replacement, content)
    if count == 0:
        print("  WARNING: Could not find footer Desk Gear <ul> to replace", file=sys.stderr)
    return new_content


# ---------------------------------------------------------------------------
# Category page update
# ---------------------------------------------------------------------------

CATEGORY_SLUG_MAP = {
    "monitor-arms": "monitor-arms.html",
    "usb-c-hubs": "usb-c-hubs.html",
    "smart-plugs": "smart-plugs.html",
    "monitor-light-bars": "monitor-light-bars.html",
    "laptop-stands": "laptop-stands.html",
    "desk-mats": "desk-mats.html",
    "desk-gear": "desk-gear.html",
}

# Category pages that use relative paths (../) vs absolute (/)
RELATIVE_REVIEWS = {
    "desk-gear.html",  # has ../reviews/ links
}


def update_category_page(filepath, products):
    """Update a category page's picks-grid with filtered products."""
    content = filepath.read_text()
    category_grid = build_category_grid(products)

    # Category pages use ../reviews/ links (relative from categories/ subdir)
    category_grid = category_grid.replace('/reviews/', '../reviews/')

    new_content = replace_picks_grid(content, category_grid)
    new_content = bump_css_version(new_content)
    filepath.write_text(new_content)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    if not DATA_FILE.exists():
        print(f"ERROR: {DATA_FILE} not found", file=sys.stderr)
        sys.exit(1)

    products = load_products()
    print(f"📦 Loaded {len(products)} products from {DATA_FILE}")
    print()

    # 1. Homepage
    print("Updating index.html...")
    new_grid = build_picks_grid(products)
    new_footer = build_footer_links(products)
    index_content = INDEX_FILE.read_text()
    index_content = bump_css_version(index_content)
    index_content = replace_picks_grid(index_content, new_grid)
    index_content = replace_footer_links(index_content, new_footer)
    INDEX_FILE.write_text(index_content)
    print(f"  ✅ index.html updated")

    # 2. Category pages
    updated_categories = set()
    for p in products:
        cat = p.get("category")
        if cat and cat in CATEGORY_SLUG_MAP:
            updated_categories.add(cat)

    for cat_slug in updated_categories:
        filename = CATEGORY_SLUG_MAP[cat_slug]
        filepath = CATEGORIES_DIR / filename
        if not filepath.exists():
            print(f"  ⚠️  {filepath} not found, skipping")
            continue
        cat_products = products_by_category(products, cat_slug)
        update_category_page(filepath, cat_products)
        print(f"  ✅ {filename} ({len(cat_products)} products)")

    print()
    print("All pages regenerated.")
    print()
    print("Next steps:")
    print("  1. Review:  git diff")
    print("  2. Commit:  git add -A && git commit -m 'Regenerate site: update product pages'")
    print("  3. Push:   git push origin main")


if __name__ == "__main__":
    main()