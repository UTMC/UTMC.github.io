"""Configuration loader for the static site generator."""

from dataclasses import dataclass, field
from pathlib import Path
import sys

if sys.version_info >= (3, 11):
    import tomllib
else:
    import tomli as tomllib


@dataclass
class Config:
    """Global site configuration from config.toml."""

    base_url: str = "https://www.utmc.or.jp"
    site_name: str = "UTMC"
    default_layout: str = "layout.html"
    files_dir: str = "files"
    layout_dir: str = "_layout"
    root_dir: Path = field(default_factory=Path)

    @classmethod
    def load(cls, config_path: Path) -> "Config":
        """Load configuration from config.toml file."""
        with open(config_path, "rb") as f:
            data = tomllib.load(f)

        config = cls(
            base_url=data.get("base_url", cls.base_url),
            site_name=data.get("site_name", cls.site_name),
            default_layout=data.get("default_layout", cls.default_layout),
            files_dir=data.get("files_dir", cls.files_dir),
            layout_dir=data.get("layout_dir", cls.layout_dir),
            root_dir=config_path.parent,
        )
        return config

    @property
    def layout_path(self) -> Path:
        """Path to the layout directory."""
        return self.root_dir / self.layout_dir

    @property
    def files_path(self) -> Path:
        """Path to the files directory."""
        return self.root_dir / self.files_dir
