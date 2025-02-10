"""Module for handling interactive diff viewing."""

import re
from typing import List

from rich import box
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.syntax import Syntax
from rich.text import Text
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, Vertical
from textual.keys import Keys
from textual.widgets import Footer, Header, RichLog, Static

from git_helper.commit_validator import validate_commit_message
from git_helper.git_utils import FileChange, get_file_diff
from git_helper.models import DiffHunk


class CommitMessage(RichLog):
    """Widget for displaying the commit message with validation."""

    def __init__(self, message: str):
        super().__init__()
        self.message = message

    def on_mount(self) -> None:
        is_valid, error_message = validate_commit_message(self.message)
        panel_style = "green" if is_valid else "red"

        # Add commit message
        self.write(
            Panel(
                Markdown(self.message),
                title="Commit Message",
                border_style=panel_style,
            )
        )

        # Add error message if invalid
        if not is_valid:
            self.write(
                Panel(
                    Markdown(error_message),
                    title="Error Message",
                    box=box.MINIMAL,
                    expand=True,
                    border_style=panel_style,
                )
            )


class FileList(RichLog):
    """Widget for displaying the list of changed files."""

    def __init__(self, changes: List[FileChange], current_file: str = None):
        super().__init__()
        self.changes = changes
        self.current_file = current_file

    def on_mount(self) -> None:
        from git_helper.formatters import format_rich_table

        table = format_rich_table(self.changes, current_file=self.current_file)
        table.columns = table.columns[:2]  # Only show file and status

        self.write(
            Panel(
                table,
                title="Modified Files",
                box=box.MINIMAL,
                expand=True,
            )
        )


class DiffView(RichLog):
    """Widget for displaying the diff content."""

    def __init__(self, content: str = "", title: str = "Diff View"):
        super().__init__()
        self.content = content
        self.view_title = title

    def on_mount(self) -> None:
        if self.content:
            # Process content
            content = self.content.expandtabs(4)
            content = re.sub(r"@@ -\d+,\d+ \+\d+,\d+ @@\n", "", content)

            syntax = Syntax(
                content,
                "diff",
                theme="monokai",
                word_wrap=True,
                tab_size=4,
            )

        else:
            syntax = Text("No changes to display")

        self.write(
            Panel(
                syntax,
                title=self.view_title,
                box=box.MINIMAL,
                expand=True,
            ),
            scroll_end=False,
        )


class DiffViewer(Static):
    """Handles the display of file diffs in a rich terminal interface."""

    CSS = """
    DiffViewer {
        layout: horizontal;
        height: 100%;
    }

    .left-panel {
        width: 30%;
        height: 100%;
    }

    .right-panel {
        width: 70%;
        height: 100%;
    }

    CommitMessage, FileList, DiffView {
        height: 100%;
        width: 100%;
        border: solid $accent;
        background: $surface;
        color: $text;
        padding: 0 1;
        overflow-y: scroll;
    }

    RichLog {
        width: 100%;
    }
    """

    def __init__(
        self,
        console: Console,
        message: str = "",
        changes: List[FileChange] = [],
        error_message: str = "",
    ):
        super().__init__()
        self.console = console
        self.changes = changes
        self.message = message
        self.error_message = error_message
        self.current_file_index = 0
        self.current_change_index = 0
        self.current_hunks: List[DiffHunk] = []

    def compose(self) -> ComposeResult:
        """Create the UI layout."""

        with Horizontal():
            # Left panel with commit message and file list
            with Vertical(classes="left-panel"):
                yield CommitMessage(self.message)
                yield FileList(self.changes, current_file=self._get_current_filename())

            # Right panel with diff view
            with Vertical(classes="right-panel"):
                if self.changes:
                    current_file = self.changes[self.current_file_index].file
                    title = f"Diff View ({current_file})"
                    if self.current_hunks:
                        title += f" - Change {self.current_change_index + 1}/{len(self.current_hunks)}"
                    yield DiffView(self._get_current_diff(), title)
                else:
                    yield DiffView()

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

    def _get_current_diff(self) -> str:
        """Get the diff for the current file."""
        if not self.current_hunks:
            diff_content = get_file_diff(
                self.changes[self.current_file_index], unified=10000
            )
            diff_content = diff_content.expandtabs(4)
            self.current_hunks = self._parse_diff_hunks(diff_content)
            self.current_change_index = 0

        if self.current_hunks:
            return self.current_hunks[self.current_change_index].content

        return "No changes to display"

    def action_next_file(self) -> None:
        """Move to next file."""
        if self.current_file_index < len(self.changes) - 1:
            self.current_file_index += 1
            self.current_change_index = 0
            self.current_hunks = []
            self.refresh(recompose=True)

    def action_prev_file(self) -> None:
        """Move to previous file."""
        if self.current_file_index > 0:
            self.current_file_index -= 1
            self.current_change_index = 0
            self.current_hunks = []
            self.refresh(recompose=True)

    def action_next_change(self) -> None:
        """Move to next change in current file."""
        if not self.current_hunks:
            diff_content = get_file_diff(self.changes[self.current_file_index])
            self.current_hunks = self._parse_diff_hunks(diff_content)

        if self.current_change_index < len(self.current_hunks) - 1:
            self.current_change_index += 1
            current_file = self.changes[self.current_file_index].file
            title = f"Diff View ({current_file}) - Change {self.current_change_index + 1}/{len(self.current_hunks)}"
            self.mount(
                DiffView(self._get_current_diff(), title),
                after=self.query_one(FileList),
            )
            self.refresh(recompose=True)

    def action_prev_change(self) -> None:
        """Move to previous change in current file."""
        if not self.current_hunks:
            diff_content = get_file_diff(self.changes[self.current_file_index])
            self.current_hunks = self._parse_diff_hunks(diff_content)

        if self.current_change_index > 0:
            self.current_change_index -= 1
            current_file = self.changes[self.current_file_index].file
            title = f"Diff View ({current_file}) - Change {self.current_change_index + 1}/{len(self.current_hunks)}"
            self.mount(
                DiffView(self._get_current_diff(), title),
                after=self.query_one(FileList),
            )
            self.refresh(layout=True)

    def action_scroll_up(self) -> None:
        """Scroll up one line."""
        self.query_one(DiffView).scroll_up()
        self.refresh(recompose=True)

    def action_scroll_down(self) -> None:
        """Scroll down one line."""
        self.query_one(DiffView).scroll_down()
        self.refresh(recompose=True)

    def action_page_up(self) -> None:
        """Scroll up one page."""
        self.query_one(DiffView).scroll_page_up()
        self.refresh(recompose=True)

    def action_page_down(self) -> None:
        """Scroll down one page."""
        self.query_one(DiffView).scroll_page_down()
        self.refresh(recompose=True)

    def action_scroll_home(self) -> None:
        """Scroll to the top of the diff view."""
        self.query_one(DiffView).scroll_home()
        self.refresh(recompose=True)

    def action_scroll_end(self) -> None:
        """Scroll to the bottom of the diff view."""
        self.query_one(DiffView).scroll_end()
        self.refresh(recompose=True)


class DiffViewerApp(App):
    """Application for reviewing changes."""

    BINDINGS = [
        Binding("q", "quit", "Quit"),
        Binding("j", "prev_change", "Previous Change"),
        Binding("k", "next_change", "Next Change"),
        Binding("h", "prev_file", "Previous File"),
        Binding("l", "next_file", "Next File"),
        Binding("left", "prev_file", "Previous File"),
        Binding("right", "next_file", "Next File"),
        # Binding("up", "scroll_up", "Scroll Up"),
        # Binding("down", "scroll_down", "Scroll Down"),
        # Binding("pageup", "page_up", "Page Up"),
        # Binding("pagedown", "page_down", "Page Down"),
        # Binding("home", "scroll_home", "Top"),
        # Binding("end", "scroll_end", "Bottom"),
    ]

    CSS = """
    Screen {
        layout: vertical;
    }

    Header {
        dock: top;
        background: $accent;
        color: $text;
        height: 1;
        content-align: center middle;
    }

    Footer {
        dock: bottom;
        background: $accent;
        color: $text;
        height: 1;
        content-align: center middle;
    }

    #key-log {
        height: 10;
        dock: bottom;
        border-top: solid $accent;
        background: $surface;
        padding: 0 1;
    }
    """

    TITLE = "Git Helper - Commit"
    SUB_TITLE = "Review Before Commit"

    def __init__(
        self,
        console: Console,
        message: str,
        changes: List[FileChange],
        error_message: str,
        show_key_log: bool = False,
    ):
        super().__init__()
        self.viewer = DiffViewer(console, message, changes, error_message)
        self.key_log = RichLog(id="key-log")
        self.show_key_log = show_key_log

    def compose(self) -> ComposeResult:
        yield Header()
        yield self.viewer
        if self.show_key_log:
            yield self.key_log
        yield Footer()

    def on_key(self, event) -> None:
        """Log all key presses."""
        self.key_log.write(f"Key pressed: {event.key}")

    def action_prev_file(self) -> None:
        """Move to previous file."""
        self.key_log.write("Action: prev_file")
        self.viewer.action_prev_file()

    def action_next_file(self) -> None:
        """Move to next file."""
        self.key_log.write("Action: next_file")
        self.viewer.action_next_file()

    def action_prev_change(self) -> None:
        """Move to previous change."""
        self.key_log.write("Action: prev_change")
        self.viewer.action_prev_change()

    def action_next_change(self) -> None:
        """Move to next change."""
        self.key_log.write("Action: next_change")
        self.viewer.action_next_change()

    def action_scroll_up(self) -> None:
        """Scroll up one line."""
        self.query_one(DiffView).scroll_up()
        self.refresh(recompose=True)

    def action_scroll_down(self) -> None:
        """Scroll down one line."""
        self.query_one(DiffView).scroll_down()
        self.refresh(recompose=True)

    def action_page_up(self) -> None:
        """Scroll up one page."""
        self.query_one(DiffView).scroll_page_up()
        self.refresh(recompose=True)

    def action_page_down(self) -> None:
        """Scroll down one page."""
        self.query_one(DiffView).scroll_page_down()
        self.refresh(recompose=True)

    def action_scroll_home(self) -> None:
        """Scroll to the top."""
        self.query_one(DiffView).scroll_home()
        self.refresh(recompose=True)

    def action_scroll_end(self) -> None:
        """Scroll to the bottom."""
        self.query_one(DiffView).scroll_end()
        self.refresh(recompose=True)


def app_diff_viewer(
    console: Console,
    message: str,
    changes: List[FileChange],
    error_message: str,
    show_key_log: bool = False,
):
    """Create a Textual app for reviewing changes."""
    app = DiffViewerApp(console, message, changes, error_message, show_key_log)
    app.run()
