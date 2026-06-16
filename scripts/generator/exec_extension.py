"""Markdown extension that embeds the output of an external command.

Per the trusted-maintainer model (see CLAUDE.md), a Markdown file may run a
helper script and embed its stdout as raw HTML using a one-line directive:

    {% exec scripts/make-timeline.py data/timeline.tsv %}

The command runs with the repository root as its working directory, so relative
paths (``scripts/...``, ``data/...``) resolve the same way as in ``update.sh``.
If the program ends in ``.py`` it is run with the current Python interpreter.
"""

import re
import shlex
import subprocess
import sys
from pathlib import Path

from markdown.extensions import Extension
from markdown.preprocessors import Preprocessor

EXEC_RE = re.compile(r"^\s*\{%\s*exec\s+(?P<command>.+?)\s*%\}\s*$")


class ExecPreprocessor(Preprocessor):
    """Replaces ``{% exec ... %}`` directives with the command's stdout."""

    def __init__(self, md, root_dir: Path) -> None:
        super().__init__(md)
        self.root_dir = root_dir

    def run(self, lines: list[str]) -> list[str]:
        new_lines: list[str] = []
        for line in lines:
            match = EXEC_RE.match(line)
            if match is None:
                new_lines.append(line)
                continue
            html = self._run_command(match.group("command"))
            # Stash as raw HTML so Markdown copies it through verbatim. strip()
            # so the leading tag is recognized as block-level (drops the <p>).
            new_lines.append(self.md.htmlStash.store(html.strip()))
        return new_lines

    def _run_command(self, command: str) -> str:
        args = shlex.split(command)
        if args and args[0].endswith(".py"):
            args = [sys.executable, *args]
        result = subprocess.run(
            args,
            cwd=self.root_dir,
            capture_output=True,
            text=True,
            check=True,
        )
        return result.stdout


class ExecExtension(Extension):
    """Registers the ``{% exec ... %}`` preprocessor."""

    def __init__(self, root_dir: Path, **kwargs) -> None:
        self.root_dir = root_dir
        super().__init__(**kwargs)

    def extendMarkdown(self, md) -> None:
        # Priority < 30 so this runs *after* normalize_whitespace, which strips
        # the STX/ETX control chars that htmlStash placeholders rely on.
        md.preprocessors.register(
            ExecPreprocessor(md, self.root_dir), "utmc_exec", priority=29
        )
