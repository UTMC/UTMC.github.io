"""Command-line interface for the static site generator."""

import argparse
import sys
from pathlib import Path

from .builder import Builder
from .config import Config


def main() -> None:
    """Main entry point for the CLI."""
    parser = argparse.ArgumentParser(description="UTMC Static Site Generator")
    parser.add_argument(
        "--config",
        "-c",
        type=Path,
        default=Path("config.toml"),
        help="Path to config.toml (default: config.toml in current directory)",
    )
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Enable verbose output",
    )

    args = parser.parse_args()

    # Resolve config file path
    config_path = args.config
    if not config_path.is_absolute():
        config_path = Path.cwd() / config_path

    if not config_path.exists():
        print(f"Error: Config file not found: {config_path}", file=sys.stderr)
        sys.exit(1)

    # Load config and build
    config = Config.load(config_path)
    builder = Builder(config)

    exit_code = builder.build()
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
