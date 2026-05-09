#!/bin/bash
# =============================================================================
# Publish Review - Validates and publishes a new review to GitHub Pages
# =============================================================================
# Run this to safely publish a review. It validates first, then commits.
# Exit codes: 0 = published, 1 = validation failed, 2 = git error
# =============================================================================

set -euo pipefail

SITE_DIR="${SITE_DIR:-$HOME/budget-tech-picks}"
REVIEW_FILE="${1:-}"
COMMIT_MSG="${2:-}"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VALIDATOR="$SCRIPT_DIR/validate-review.sh"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# =============================================================================
# Usage
# =============================================================================

usage() {
    echo "Usage: $0 <review-file.html> [commit-message]"
    echo ""
    echo "Validates a review and commits to GitHub Pages if it passes."
    echo ""
    echo "Example:"
    echo "  $0 reviews/new-monitor-arm.html \"Add review: Ergotron LX Monitor Arm\""
    exit 1
}

# Check args
if [[ -z "$REVIEW_FILE" ]]; then
    usage
fi

# =============================================================================
# Validation Phase
# =============================================================================

echo ""
echo "=============================================="
echo "  Phase 1: Validation"
echo "=============================================="
echo ""

# Resolve full path
if [[ ! "$REVIEW_FILE" = /* ]]; then
    REVIEW_FILE="$SITE_DIR/$REVIEW_FILE"
fi

if [[ ! -f "$REVIEW_FILE" ]]; then
    echo -e "${RED}✗ File not found: $REVIEW_FILE${NC}"
    exit 1
fi

# Run validator
echo "Running validation checks..."
echo ""

"$VALIDATOR" "$REVIEW_FILE"
validation_result=$?

if [[ $validation_result -ne 0 ]]; then
    echo ""
    echo -e "${RED}✗ VALIDATION FAILED${NC}"
    echo "  The review did not pass validation."
    echo "  Fix the errors above and try again."
    echo ""
    echo "  To run with --force to skip validation:"
    echo "  $0 --force <review-file.html>"
    exit 1
fi

echo ""
echo -e "${GREEN}✓ Validation passed!${NC}"
echo ""

# =============================================================================
# Git Phase
# =============================================================================

echo "=============================================="
echo "  Phase 2: Git Commit & Push"
echo "=============================================="
echo ""

cd "$SITE_DIR"

# Check git status
if [[ -n $(git status --porcelain) ]]; then
    echo "Changes detected in working directory."
else
    echo "No changes to commit."
    exit 0
fi

# Stage the file
git add "$REVIEW_FILE"
echo "Staged: $(basename "$REVIEW_FILE")"

# Default commit message if not provided
if [[ -z "$COMMIT_MSG" ]]; then
    PRODUCT_NAME=$(grep -o '<title>[^<]*</title>' "$REVIEW_FILE" | sed 's/<[^>]*>//g' | sed 's/ Review — Home Office Stack//')
    COMMIT_MSG="Add review: $PRODUCT_NAME"
fi

# Commit
git commit -m "$COMMIT_MSG"
echo ""
echo "Committed: $COMMIT_MSG"

# Push
echo ""
echo "Pushing to origin..."
git push origin main
echo ""

echo "=============================================="
echo -e "  ${GREEN}✓ PUBLISHED SUCCESSFULLY${NC}"
echo "=============================================="
echo ""
echo "  Review will be live on GitHub Pages in ~1-2 minutes."
echo "  URL: https://homeofficestack.com/reviews/$(basename "$REVIEW_FILE" .html).html"
echo ""

exit 0