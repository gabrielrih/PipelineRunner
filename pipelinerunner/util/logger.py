import os
import logging
import logging.config

from rich.console import Console
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn, TimeElapsedColumn
from rich.theme import Theme
from typing import Dict

from pipelinerunner.util.json import to_pretty_json


LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')


class Logger:
    @staticmethod
    def get_logger(name):
        logger = logging.getLogger(name)
        logger.setLevel(level=LOG_LEVEL)
        handler = logging.StreamHandler()
        handler.setLevel(LOG_LEVEL)
        formatter = logging.Formatter("%(levelname)s: %(message)s")
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        return logger


class BetterLogger:
    _console = Console(theme=Theme({
        "info": "cyan",
        "success": "green",
        "warning": "yellow",
        "error": "bold red",
        "debug": "dim"
    }))

    LEVELS = {
        "debug": 10,
        "info": 20,
        "warning": 30,
        "error": 40
    }

    DEFAULT_MIN_LEVEL = 'debug'
    MIN_LEVEL = LEVELS.get(os.getenv('LOG_LEVEL', DEFAULT_MIN_LEVEL).lower(), LEVELS[DEFAULT_MIN_LEVEL])

    @classmethod
    def get_logger(cls, name: str):
        return cls()

    def _should_log(self, level: str) -> bool:
        return self.LEVELS[level] >= self.MIN_LEVEL

    def info(self, message: str):
        if self._should_log("info"):
            self._console.print(f"[info]ℹ️  {message}")

    def success(self, message: str):
        if self._should_log("info"):  # success == info
            self._console.print(f"[success]✅ {message}")

    def warning(self, message: str):
        if self._should_log("warning"):
            self._console.print(f"[warning]⚠️  {message}")

    def error(self, message: str):
        if self._should_log("error"):
            self._console.print(f"[error]❌ {message}")

    def debug(self, message: str):
        if self._should_log("debug"):
            self._console.print(f"[debug]🐞 {message}")

    def print_json(self, content: Dict):
        json_str = to_pretty_json(content)  # Dict to json
        self._console.print_json(json_str)

    @classmethod
    def progress(cls, description: str):
        """Context manager for progress bar usage"""
        return Progress(
            SpinnerColumn(),
            TextColumn("[cyan]{task.description}"),
            TimeElapsedColumn(),
            transient = False,
            console = cls._console
        )

    @classmethod
    def print_table(cls, title: str, columns: list[str], rows: list[list[str]]):
        table = Table(title=title)
        for col in columns:
            table.add_column(col, style="cyan", no_wrap=True)
        for row in rows:
            table.add_row(*[str(cell) for cell in row])
        cls._console.print(table)
