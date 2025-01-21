"""Module for handling interactive diff viewing."""

import os
import re
from dataclasses import dataclass
from typing import List

import readchar
from rich.box import MINIMAL
from rich.console import Console
from rich.layout import Layout
from rich.live import Live
from rich.markdown import Markdown
from rich.panel import Panel
from rich.syntax import Syntax
from rich.text import Text

from git_helper.commit_validator import validate_commit_message
from git_helper.git_utils import FileChange, get_file_diff
from git_helper.models import DiffHunk


class DiffViewer:
    """Handles the display of file diffs in a rich terminal interface."""

    def __init__(self, console: Console):
        self.console = console
        self.current_file_index = 0
        self.current_change_index = 0
        self.changes: List[FileChange] = []
        self.current_hunks: List[DiffHunk] = []

    def create_layout(
        self, message: str, changes: List[FileChange], error_message: str = ""
    ) -> Layout:
        """Create the split layout with commit message, changes table, and diff view."""
        self.changes = changes

        # Create main layout
        layout = Layout()

        # Create left and right sections
        left_layout = Layout(name="left", ratio=1)
        right_layout = Layout(name="right", ratio=2)

        # Split main layout into left and right
        layout.split_row(left_layout, right_layout)

        # Split left panel into message and table
        left_top = Layout(name="left_top", ratio=2)
        left_bottom = Layout(name="left_bottom", ratio=3)
        left_layout.split_column(left_top, left_bottom)

        # Add commit message to left top panel with validation color
        is_valid, error_message = validate_commit_message(message)

        # Add validation error message to left top panel
        panel_style = "green" if is_valid else "red"
        left_top_message = Panel(
            Markdown(message),
            title="Commit Message",
            border_style=panel_style,
        )
        left_top_error = (
            Panel(
                Markdown(error_message),
                box=MINIMAL,
                title="Error Message",
                border_style=panel_style,
            )
            if not is_valid
            else Panel("", box=MINIMAL)
        )
        left_top.split_column(
            Layout(left_top_message, ratio=3), Layout(left_top_error, ratio=1)
        )

        # Add changes table to left bottom panel
        from git_helper.formatters import format_rich_table

        table = format_rich_table(
            changes,
            current_file=changes[self.current_file_index].file if changes else None,
        )
        table.columns = table.columns[:4]
        left_bottom.update(
            Panel(
                table,
                box=MINIMAL,
                title="Modified Files",
            )
        )

        # Add diff view to right panel
        if changes:
            syntax = self._get_current_diff()
            right_layout.update(
                Panel(
                    syntax,
                    title=f"Diff View ({changes[self.current_file_index].file}) - Change {self.current_change_index + 1}/{len(self.current_hunks)}",
                    border_style="blue",
                    expand=True,
                    padding=(0, 1),
                )
            )
        else:
            right_layout.update(
                Panel(
                    Text("No changes to display"),
                    title="Diff View",
                )
            )

        return layout

    def _get_current_filename(self) -> str:
        """Get the current file being displayed."""
        if not self.changes:
            return "No files"
        return self.changes[self.current_file_index].file

    def _parse_diff_hunks(self, diff_content: str) -> List[DiffHunk]:
        """Parse diff content into separate hunks."""
        hunks = []
        current_hunk = []
        current_start = 0
        in_hunk = False

        for line in diff_content.splitlines():
            # Strip ANSI escape codes from the line
            bare_line = re.sub(r"\x1b\[[0-9;]*[mG]", "", line.strip())

            if bare_line.startswith("diff --git"):
                continue  # Skip diff header
            if bare_line.startswith("@@"):
                # New hunk found, save previous if exists
                if current_hunk:
                    hunks.append(DiffHunk(current_start, "\n".join(current_hunk)))
                # Parse the @@ line to get starting line number
                match = re.search(r"@@ -(\d+)", line)
                current_start = int(match.group(1)) if match else 0
                current_hunk = [line]
                in_hunk = True
            elif in_hunk:
                current_hunk.append(line)

        # Add the last hunk
        if current_hunk:
            hunks.append(DiffHunk(current_start, "\n".join(current_hunk)))

        return hunks

    def _get_current_diff(self) -> Syntax:
        """Get the diff for the current file."""
        # Get the diff content
        if not self.current_hunks:
            diff_content = get_file_diff(self.changes[self.current_file_index])
            # Process content before parsing hunks
            diff_content = diff_content.expandtabs(4)
            self.current_hunks = self._parse_diff_hunks(diff_content)
            self.current_change_index = 0

        if self.current_hunks:
            content = self.current_hunks[self.current_change_index].content
            # Process hunk content before syntax highlighting
            content = content.expandtabs(4)
            if "\x1b[" in content:
                content = re.sub(r"\x1b\[[0-9;]*[mG]", "", content)
            return Syntax(
                content,
                "diff",
                theme="ansi_dark",  # Use consistent theme
                word_wrap=True,
                tab_size=4,
            )

        return Syntax("No changes to display", "text")

    def next_file(self) -> bool:
        """Move to next file. Returns True if moved."""
        if self.current_file_index < len(self.changes) - 1:
            self.current_file_index += 1
            self.current_change_index = 0
            self.current_hunks = []
            return True
        return False

    def prev_file(self) -> bool:
        """Move to previous file. Returns True if moved."""
        if self.current_file_index > 0:
            self.current_file_index -= 1
            self.current_change_index = 0
            self.current_hunks = []
            return True
        return False

    def next_change(self) -> bool:
        """Move to next change in current file. Returns True if moved."""
        if not self.current_hunks:
            diff_content = get_file_diff(self.changes[self.current_file_index])
            self.current_hunks = self._parse_diff_hunks(diff_content)

        if self.current_change_index < len(self.current_hunks) - 1:
            self.current_change_index += 1
            return True
        return False

    def prev_change(self) -> bool:
        """Move to previous change in current file. Returns True if moved."""
        if not self.current_hunks:
            diff_content = get_file_diff(self.changes[self.current_file_index])
            self.current_hunks = self._parse_diff_hunks(diff_content)

        if self.current_change_index > 0:
            self.current_change_index -= 1
            return True
        return False

def layout_diff_viewer(console: Console, message: str, changes: List[FileChange], error_message: str):
    """Create a layout for the diff viewer."""
    viewer = DiffViewer(console)
    layout = viewer.create_layout(message, changes, error_message)
    with Live(layout, refresh_per_second=4, screen=True) as live:
        while True:
            # Read a key
            key = readchar.readkey()

            # Handle navigation keys
            if key == readchar.key.LEFT:
                if viewer.prev_change():
                    layout = viewer.create_layout(message, changes, error_message)
                    live.update(layout)
            elif key == readchar.key.RIGHT:
                if viewer.next_change():
                    layout = viewer.create_layout(message, changes, error_message)
                    live.update(layout)
            elif key == readchar.key.UP:
                if viewer.prev_file():
                    layout = viewer.create_layout(message, changes, error_message)
                    live.update(layout)
            elif key == readchar.key.DOWN:
                if viewer.next_file():
                    layout = viewer.create_layout(message, changes, error_message)
                    live.update(layout)
            elif key in ("q", "Q", readchar.key.CTRL_C):
                break
            elif key == " ":
                if viewer.next_change():
                    layout = viewer.create_layout(message, changes, error_message)
                    live.update(layout)
