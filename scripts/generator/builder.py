"""Main build orchestrator."""

import sys
from pathlib import Path
from typing import Iterator

from .config import Config
from .page import Page
from .renderer import Renderer
from .validators import PageValidator, SiteValidator, ValidationError


class Builder:
    """Main build orchestrator."""

    # Directories to skip when discovering pages
    SKIP_DIRS = {"scripts", "node_modules", "data"}

    # Files to skip (documentation files that shouldn't be converted)
    SKIP_FILES = {"CLAUDE.md", "README.md", "CHANGELOG.md", "LICENSE.md"}

    def __init__(self, config: Config) -> None:
        self.config = config
        self.renderer = Renderer(config)
        self.page_validator = PageValidator(config)
        self.site_validator = SiteValidator()

    def discover_pages(self) -> Iterator[Path]:
        """Find all Markdown files to process."""
        for md_file in self.config.root_dir.glob("**/*.md"):
            relative = md_file.relative_to(self.config.root_dir)
            parts = relative.parts

            # Skip files in special directories
            if any(
                p.startswith(("_", ".")) or p in self.SKIP_DIRS for p in parts
            ):
                continue

            # Skip documentation files
            if md_file.name in self.SKIP_FILES:
                continue

            yield md_file

    def build(self) -> int:
        """Build the entire site. Returns exit code (0 for success)."""
        print("Starting build...")

        # Discover and load all pages
        pages: list[Page] = []
        all_errors: list[ValidationError] = []
        all_warnings: list[ValidationError] = []

        for md_path in self.discover_pages():
            rel_path = md_path.relative_to(self.config.root_dir)
            print(f"  Processing: {rel_path}")

            try:
                page = Page.from_file(md_path, self.config.root_dir, self.config)

                # Validate individual page
                result = self.page_validator.validate(page)
                all_errors.extend(result.errors)
                all_warnings.extend(result.warnings)

                pages.append(page)
            except Exception as e:
                all_errors.append(
                    ValidationError(md_path, f"Failed to parse: {e}", is_fatal=True)
                )

        if not pages:
            print("No Markdown files found to process.")
            return 0

        # Site-wide validation
        dup_result = self.site_validator.validate_no_duplicate_outputs(pages)
        all_errors.extend(dup_result.errors)

        # Report warnings
        for warning in all_warnings:
            rel_path = warning.path.relative_to(self.config.root_dir)
            print(f"  WARNING: {rel_path}: {warning.message}", file=sys.stderr)

        # Check for fatal errors
        fatal_errors = [e for e in all_errors if e.is_fatal]
        if fatal_errors:
            print("\nBuild FAILED with errors:", file=sys.stderr)
            for error in fatal_errors:
                rel_path = error.path.relative_to(self.config.root_dir)
                print(f"  ERROR: {rel_path}: {error.message}", file=sys.stderr)
            return 1

        # Render and write all pages
        for page in pages:
            html = self.renderer.render_page(page)

            # Ensure output directory exists
            page.output_path.parent.mkdir(parents=True, exist_ok=True)

            # Write output
            page.output_path.write_text(html, encoding="utf-8")
            rel_output = page.output_path.relative_to(self.config.root_dir)
            print(f"  Generated: {rel_output}")

        print(f"\nBuild completed successfully: {len(pages)} page(s) generated.")
        return 0
