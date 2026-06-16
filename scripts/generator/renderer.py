"""Markdown and template rendering."""

from typing import TYPE_CHECKING

import markdown
from jinja2 import Environment, FileSystemLoader

from .exec_extension import ExecExtension

if TYPE_CHECKING:
    from .config import Config
    from .page import Page


class Renderer:
    """Renders Markdown content through Jinja2 templates."""

    def __init__(self, config: "Config") -> None:
        self.config = config

        # Initialize Markdown with extensions
        self.md = markdown.Markdown(
            extensions=[
                "extra",  # Tables, fenced code, footnotes, etc.
                "toc",  # Table of contents
                ExecExtension(root_dir=config.root_dir),  # {% exec ... %}
            ],
            output_format="html5",
        )

        # Initialize Jinja2 environment
        self.env = Environment(
            loader=FileSystemLoader(config.layout_path),
            autoescape=False,  # We trust Markdown content (per CLAUDE.md)
            trim_blocks=True,
            lstrip_blocks=True,
        )

    def render_markdown(self, content: str) -> str:
        """Convert Markdown to HTML."""
        self.md.reset()
        return self.md.convert(content)

    def render_page(self, page: "Page") -> str:
        """Render a complete page through its template."""
        # Convert Markdown content to HTML
        html_content = self.render_markdown(page.content)

        # Load and render template
        template = self.env.get_template(page.layout)

        full_canonical_url = f"{self.config.base_url}{page.canonical_url}"

        return template.render(
            title=page.title,
            site_name=page.site_name,
            description=page.description or "",
            content=html_content,
            canonical_url=full_canonical_url,
            og_image_url=page.og_image_url or "",
            base_url=self.config.base_url,
            page=page,
        )
