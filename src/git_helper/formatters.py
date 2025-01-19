"""Formatting utilities for git workflow."""

from typing import List

from rich.table import Table

from .models import FileChange


def format_rich_table(changes: List[FileChange]) -> Table:
    """Format changes into a rich table."""
    if not changes:
        return None

    table = Table(title="Modified Files")
    table.add_column("File", style="cyan")
    table.add_column("Status", style="magenta")
    table.add_column("Added", justify="right", style="green")
    table.add_column("Removed", justify="right", style="red")
    table.add_column("% Changed", justify="right")
    table.add_column("Description")

    for change in changes:
        table.add_row(
            change.file,
            change.status2 + '/' + change.status,
            str(change.added_lines),
            str(change.removed_lines),
            f"{change.percent_changed:.1f}%",
            change.description or "",
        )

    return table


def format_markdown_table(changes: List[FileChange]) -> str:
    """Format changes into a markdown table with consistent column widths."""
    if not changes:
        return "No changes detected."

    # Define column headers and widths
    headers = ["File", "Status", "Added", "Removed", "% Changed", "Description"]
    rows = [
        [
            change.file,
            change.status2 + '/' + change.status,
            str(change.added_lines),
            str(change.removed_lines),
            f"{change.percent_changed:.1f}%",
            change.description,
        ]
        for change in changes
    ]

    # Calculate column widths
    widths = [len(h) for h in headers]
    for row in rows:
        for i, cell in enumerate(row):
            widths[i] = max(widths[i], len(cell))

    # Format table
    sep = "|".join("-" * (w + 2) for w in widths)
    header = "|".join(f" {h:<{w}} " for h, w in zip(headers, widths))

    table_rows = [
        "|".join(f" {cell:<{w}} " for cell, w in zip(row, widths)) for row in rows
    ]

    return f"""|{header}|
|{sep}|
""" + "\n".join(f"|{row}|" for row in table_rows)
