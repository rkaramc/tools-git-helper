"""Data models for git workflow."""

from typing import NamedTuple


class FileChange(NamedTuple):
    file: str
    status: str
    added_lines: int
    removed_lines: int
    percent_changed: float
    description: str = ""
