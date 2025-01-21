"""Data models for git workflow."""

from dataclasses import dataclass


@dataclass
class FileChange:
    file: str
    status2: str
    status: str
    added_lines: int
    removed_lines: int
    percent_changed: float
    description: str = ""


@dataclass
class DiffHunk:
    """Represents a single change hunk in a diff."""

    start_line: int
    content: str
