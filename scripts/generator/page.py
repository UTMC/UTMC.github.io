"""Page class representing a Markdown source file."""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

import frontmatter

from .config import Config


@dataclass
class Page:
    """Represents a single Markdown page with its metadata."""

    source_path: Path
    root_dir: Path

    # Frontmatter fields
    title: str = ""
    site_name: Optional[str] = None
    description: Optional[str] = None
    image: Optional[str] = None
    layout: Optional[str] = None

    # Content
    content: str = ""

    # Computed fields
    output_path: Path = field(default_factory=Path)
    canonical_url: str = ""
    og_image_url: Optional[str] = None

    def __post_init__(self) -> None:
        """Compute derived paths after initialization."""
        self._compute_paths()

    def _compute_paths(self) -> None:
        """Compute output path and canonical URL based on source path."""
        # /path/to/page.md -> /path/to/page.html
        self.output_path = self.source_path.with_suffix(".html")

        # Compute canonical URL path
        relative = self.output_path.relative_to(self.root_dir)
        url_path = "/" + str(relative).replace("\\", "/")

        # Handle index.html -> directory URL with trailing slash
        if url_path.endswith("/index.html"):
            url_path = url_path[:-10]  # Remove "index.html", keep trailing slash
            if url_path == "":
                url_path = "/"
        else:
            # Remove .html extension for non-index pages
            url_path = url_path[:-5]  # Remove ".html"

        self.canonical_url = url_path

    @classmethod
    def from_file(cls, path: Path, root_dir: Path, config: Config) -> "Page":
        """Load a page from a Markdown file."""
        post = frontmatter.load(path)

        page = cls(
            source_path=path,
            root_dir=root_dir,
            title=post.get("title", ""),
            site_name=post.get("site_name"),
            description=post.get("description"),
            image=post.get("image"),
            layout=post.get("layout"),
            content=post.content,
        )

        # Apply defaults from config
        if page.site_name is None:
            page.site_name = config.site_name
        if page.layout is None:
            page.layout = config.default_layout

        # Compute OGP image URL
        if page.image:
            page.og_image_url = f"{config.base_url}/{config.files_dir}/{page.image}"
        else:
            page.og_image_url = None

        return page
