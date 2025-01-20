"""Command line interface for git workflow."""

import logging
import os

import click
import git
import readchar
from rich.console import Console
from rich.live import Live
from rich.markdown import Markdown

from git_helper.diff_viewer import DiffViewer

from .commit_validator import (
    format_validation_error,
    validate_commit_message,
)
from .file_utils import (
    get_commit_message_from_pending_file,
    # read_pending_changes,
    set_commit_message_to_pending_file,
    update_pending_changes,
    # write_pending_changes,
)
from .formatters import format_rich_table
from .git_utils import get_file_changes, get_repo_root

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

console = Console()


@click.group()
def cli():
    """Git Workflow Tool - A structured approach to git commits."""
    logger.debug("git workflow tool -> cli")
    pass


@cli.command()
def prepare():
    """Generate pending-changes.md with current changes."""
    logger.debug("git workflow tool -> cli -> prepare")
    _prepare()


def _prepare():
    repo_path = get_repo_root()
    changes = get_file_changes(repo_path)
    update_pending_changes(repo_path, changes)
    console.print(
        f"\n[green]Updated[/green] {os.path.join(repo_path, 'pending-changes.md')} with current changes."
    )


@cli.command()
def review():
    """Review pending changes and commit message."""
    logger.debug("git workflow tool -> cli -> review")
    _review()


def _review():
    repo_path = get_repo_root()
    changes = get_file_changes(repo_path, cached_only=True)

    if not changes:
        console.print("[yellow]No changes detected[/yellow]")
        return

    pending_file = os.path.join(repo_path, "pending-changes.md")
    if not os.path.exists(pending_file):
        _prepare()

    if os.path.exists(pending_file):
        message = get_commit_message_from_pending_file(pending_file)
        is_valid, error_message = validate_commit_message(message)
        if not is_valid:
            error_message += "\n" + format_validation_error(error_message)
        md = Markdown(message)
        console.print(md)

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


@cli.command()
@click.option("--message", "-m", help="Commit message")
def message(message: str):
    """Use Cascade AI to generate commit message."""
    logger.debug("git workflow tool -> cli -> message")
    _message(message)


def _message(message: str):
    logger.debug("generate commit message")
    repo_path = get_repo_root()
    changes = get_file_changes(repo_path)

    if not changes:
        console.print("[yellow]No changes detected[/yellow]")
        return

    if not message:
        console.print(
            "[yellow]Note:[/yellow] This feature requires Cascade AI integration"
        )
        console.print(
            "Please use the Cascade AI assistant to generate your commit message"
        )
        return
    else:
        console.print(f"[green]New commit message:[/green] {message}")

    pending_file = os.path.join(repo_path, "pending-changes.md")
    if not os.path.exists(pending_file):
        _prepare()

    if os.path.exists(pending_file):
        message = message or get_commit_message_from_pending_file(pending_file)
        is_valid, error_message = validate_commit_message(message)
        if not is_valid:
            console.print(f"[red]Error:[/red] {error_message}")
            console.print(format_validation_error(error_message))
            raise click.Abort()

        set_commit_message_to_pending_file(pending_file, message)
        console.print(f"[green]Updated[/green] {pending_file} with commit message")

    _review()


@cli.command()
@click.option("--amend", is_flag=True, help="Amend the previous commit")
@click.argument("message", required=False)
def commit(message: str, amend: bool):
    """Commit changes with the specified message."""
    logger.debug("git workflow tool -> cli -> commit")
    _commit(message, amend)


def _commit(message: str, amend: bool):
    repo_path = get_repo_root()

    if not message:
        pending_file = os.path.join(repo_path, "pending-changes.md")
        if not os.path.exists(pending_file):
            prepare()

        if os.path.exists(pending_file):
            message = get_commit_message_from_pending_file(pending_file)

    if not message:
        console.print("[red]Error:[/red] No commit message provided")
        raise click.Abort()

    valid_message = validate_commit_message(message)
    if not valid_message:
        console.print("[red]Error:[/red] Commit message is not valid")
        raise click.Abort()

    console.print(f"[green]Commit message:[/green] {message}")
    user_confirmation = click.confirm(
        "Are you sure you want to commit these changes?", default=True
    )
    if not user_confirmation:
        console.print("[yellow]Commit aborted by user.[/yellow]")
        raise click.Abort()

    repo = git.Repo(repo_path)
    if amend:
        repo.index.commit(message, amend=True)
    else:
        repo.index.commit(message)

    # Clean up pending-changes.md
    pending_file = os.path.join(repo_path, "pending-changes.md")
    if os.path.exists(pending_file):
        os.remove(pending_file)

    console.print("[green]Changes committed successfully![/green]")
