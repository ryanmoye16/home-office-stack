#!/bin/bash
# =============================================================================
# Review Validator - Deterministic validation for affiliate review pages
# =============================================================================
# Run this BEFORE committing any review to catch errors automatically.
# Exit codes: 0 = pass, 1 = validation error, 2 = critical error
# =============================================================================

set -euo pipefail

SITE_DIR="${SITE_DIR:-$HOME/budget-tech-picks}"
REVIEW_FILE="${1:-}"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

ERRORS=0
WARNINGS=0

# =============================================================================
# Helper functions
# =============================================================================

log_error() {
    echo -e "${RED}✗ ERROR:${NC} $1"
    ERRORS=$((ERRORS + 1))
}

log_warn() {
    echo -e "${YELLOW}⚠ WARNING:${NC} $1"
    WARNINGS=$((WARNINGS + 1))
}

log_ok() {
    echo -e "${GREEN}✓${NC} $1"
}

log_info() {
    echo -e "  → $1"
}

# =============================================================================
# Main validation
# =============================================================================

validate_review() {
    local file="$1"
    
    echo "=============================================="
    echo "  Review Validator"
    echo "  File: $(basename "$file")"
    echo "=============================================="
    echo ""
    
    # Check file exists
    if [[ ! -f "$file" ]]; then
        log_error "File does not exist: $file"
        return 1
    fi
    
    # =========================================================================
    # SECTION 1: Required HTML elements
    # =========================================================================
    echo "--- Required HTML Elements ---"
    
    if grep -q '<!DOCTYPE html>' "$file"; then
        log_ok "DOCTYPE present"
    else
        log_error "Missing DOCTYPE"
    fi
    
    if grep -q '<meta charset="UTF-8">' "$file"; then
        log_ok "UTF-8 charset declared"
    else
        log_error "Missing UTF-8 charset"
    fi
    
    if grep -q '<meta name="description"' "$file"; then
        log_ok "Meta description present"
    else
        log_error "Missing meta description"
    fi
    
    if grep -q '<title>.*Review — Home Office Stack</title>' "$file"; then
        log_ok "Title format correct"
    else
        log_error "Title missing or incorrect format (should end with 'Review — Home Office Stack')"
    fi
    
    # =========================================================================
    # SECTION 2: JSON-LD Schema Validation
    # =========================================================================
    echo ""
    echo "--- JSON-LD Schema ---"
    
    if ! grep -q 'type="application/ld+json"' "$file"; then
        log_error "Missing JSON-LD script tag"
    else
        log_ok "JSON-LD script tag present"
        
        # Extract JSON-LD content and validate structure
        local json_content=$(sed -n '/<script type="application\/ld+json">/,/<\/script>/p' "$file" | sed '1d;$d')
        
        # Check required fields in schema
        if echo "$json_content" | grep -q '"@type": "Review"'; then
            log_ok "Schema type: Review"
        else
            log_error "JSON-LD missing '@type': 'Review'"
        fi
        
        if echo "$json_content" | grep -q '"name":' "$file"; then
            log_ok "Product name present"
        else
            log_error "JSON-LD missing product 'name'"
        fi
        
        if echo "$json_content" | grep -q '"sku":'; then
            log_ok "SKU (ASIN) present"
        else
            log_error "JSON-LD missing product 'sku' (ASIN)"
        fi
        
        if echo "$json_content" | grep -q '"image":'; then
            log_ok "Product image present"
        else
            log_error "JSON-LD missing product 'image'"
        fi
        
        if echo "$json_content" | grep -q '"reviewRating"'; then
            log_ok "Review rating present"
        else
            log_error "JSON-LD missing 'reviewRating'"
        fi
        
        if echo "$json_content" | grep -q '"datePublished"'; then
            log_ok "Date published present"
        else
            log_error "JSON-LD missing 'datePublished'"
        fi
    fi
    
    # =========================================================================
    # SECTION 3: Amazon Affiliate Tag
    # =========================================================================
    echo ""
    echo "--- Amazon Affiliate Tag ---"
    
    # Check for WRONG tag
    if grep -q 'tag=budgettechp08-20' "$file" || grep -q 'tag=budget-tech-picks' "$file"; then
        log_error "WRONG Amazon tag detected! Should be 'homeofficestack-20'"
    else
        log_ok "No old/wrong Amazon tags found"
    fi
    
    # Check for CORRECT tag
    if grep -q 'tag=homeofficestack-20' "$file"; then
        log_ok "Correct Amazon tag 'homeofficestack-20' present"
    else
        log_error "Missing correct Amazon tag 'homeofficestack-20'"
    fi
    
    # =========================================================================
    # SECTION 4: Brand Name Compliance
    # =========================================================================
    echo ""
    echo "--- Brand Name Compliance ---"
    
    if grep -qi 'Budget Tech Picks' "$file"; then
        log_error "Brand leak: 'Budget Tech Picks' found in content!"
    else
        log_ok "No brand leak ('Budget Tech Picks')"
    fi
    
    if grep -qi 'homeofficestack' "$file"; then
        log_ok "Brand name 'Home Office Stack' found"
    else
        log_warn "Brand name 'Home Office Stack' not found in content"
    fi
    
    # =========================================================================
    # SECTION 5: Disclosure Check
    # =========================================================================
    echo ""
    echo "--- Affiliate Disclosure ---"
    
    if grep -q 'We may earn from qualifying purchases via affiliate links' "$file"; then
        log_ok "Affiliate disclosure present in footer"
    else
        log_error "Missing affiliate disclosure in footer"
    fi
    
    # =========================================================================
    # SECTION 6: Required Review Sections
    # =========================================================================
    echo ""
    echo "--- Required Review Sections ---"
    
    local required_sections=(
        "Our Verdict"
        "Specifications"
        "What We Liked"
        "What Could Be Better"
        "Bottom Line"
    )
    
    for section in "${required_sections[@]}"; do
        if grep -q "<h2>${section}</h2>" "$file" || grep -q "<h2>${section}" "$file"; then
            log_ok "Section: $section"
        else
            log_error "Missing required section: $section"
        fi
    done
    
    # =========================================================================
    # SECTION 7: Image Validation
    # =========================================================================
    echo ""
    echo "--- Image URLs ---"
    
    # Check if product images use Amazon CDN
    local img_count=$(grep -o 'https://m.media-amazon.com/images/I/[a-zA-Z0-9._-]*\.jpg' "$file" | wc -l)
    if [[ $img_count -gt 0 ]]; then
        log_ok "Amazon product images found: $img_count"
    else
        log_warn "No Amazon CDN images found"
    fi
    
    # =========================================================================
    # SECTION 8: Price Format
    # =========================================================================
    echo ""
    echo "--- Price Format ---"
    
    # Check for price in metadata section
    if grep -q 'Price:</span>' "$file"; then
        log_ok "Price displayed in review metadata"
    else
        log_warn "Price not found in review metadata"
    fi
    
    # =========================================================================
    # SECTION 9: Category Link
    # =========================================================================
    echo ""
    echo "--- Category Links ---"
    
    if grep -q 'href=".*categories/.*\.html"' "$file"; then
        log_ok "Category link present"
    else
        log_warn "No category link found"
    fi
    
    # =========================================================================
    # SECTION 10: Accessibility Checks
    # =========================================================================
    echo ""
    echo "--- Accessibility ---"
    
    # Check for alt tags on images
    local images_without_alt=$(grep -o '<img[^>]*>' "$file" | grep -v 'alt=' | wc -l)
    if [[ $images_without_alt -eq 0 ]]; then
        log_ok "All images have alt attributes"
    else
        log_warn "$images_without_alt image(s) missing alt attributes"
    fi
    
    # Check for lazy loading on images
    if grep -q 'loading="lazy"' "$file"; then
        log_ok "Lazy loading present on images"
    else
        log_warn "No lazy loading found on images"
    fi
    
    # =========================================================================
    # SUMMARY
    # =========================================================================
    echo ""
    echo "=============================================="
    echo "  Validation Summary"
    echo "=============================================="
    echo ""
    echo -e "  Errors:   ${RED}$ERRORS${NC}"
    echo -e "  Warnings: ${YELLOW}$WARNINGS${NC}"
    echo ""
    
    if [[ $ERRORS -eq 0 ]]; then
        echo -e "${GREEN}✓ VALIDATION PASSED${NC}"
        echo "  Ready to publish."
        return 0
    else
        echo -e "${RED}✗ VALIDATION FAILED${NC}"
        echo "  Fix errors before publishing."
        return 1
    fi
}

# =============================================================================
# Run validation
# =============================================================================

if [[ -z "$REVIEW_FILE" ]]; then
    echo "Usage: ./validate-review.sh <review-file.html>"
    echo ""
    echo "Validates a review HTML file for:"
    echo "  - Required HTML elements"
    echo "  - JSON-LD schema correctness"
    echo "  - Amazon affiliate tag"
    echo "  - Brand name compliance"
    echo "  - Required review sections"
    echo "  - Disclosure presence"
    exit 1
fi

validate_review "$REVIEW_FILE"
exit_code=$?

exit $exit_code