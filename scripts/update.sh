#!/usr/bin/env bash
set -euo pipefail

# UTMC Website Build Script
# Must be run from repository root

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(dirname "$SCRIPT_DIR")"

# Verify we're in the repository root
if [[ ! -f "$ROOT_DIR/config.toml" ]]; then
    echo "Error: config.toml not found. Run this script from the repository root." >&2
    exit 1
fi

cd "$ROOT_DIR"

echo "=== UTMC Website Build ==="
echo "Root directory: $ROOT_DIR"
echo ""

# Step 1: Sync dependencies
echo "Step 1: Syncing dependencies..."
cd "$SCRIPT_DIR"
uv sync
cd "$ROOT_DIR"

# Step 2: Run the static site generator
# (The timeline section is generated during this step via the {% exec %}
# directive in history.md; see scripts/make-timeline.py.)
echo ""
echo "Step 2: Generating HTML from Markdown..."
cd "$SCRIPT_DIR"
uv run python -m generator.cli --config "$ROOT_DIR/config.toml"
BUILD_EXIT_CODE=$?
cd "$ROOT_DIR"

if [[ $BUILD_EXIT_CODE -ne 0 ]]; then
    echo ""
    echo "Build FAILED with exit code $BUILD_EXIT_CODE" >&2
    exit $BUILD_EXIT_CODE
fi

echo ""
echo "=== Build completed successfully ==="
