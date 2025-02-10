"""Command line interface for git workflow."""

import logging
import os

import click
from git.cmd import Git
from rich.console import Console
from rich.markdown import Markdown

from git_helper.commit_validator import (
    format_validation_error,
    validate_commit_message,
)
from git_helper.diff_viewer import app_diff_viewer
from git_helper.file_utils import (
    get_commit_message_from_pending_file,
    get_pending_file_path,
    update_pending_changes,
)
from git_helper.git_utils import get_file_changes, get_repo_root

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

console = Console()


@click.group()
def cli():
    """Git Workflow Tool - A structured approach to git commits."""
    logger.debug("git workflow tool -> cli")
    pass


def _prepare(message: str = None):
    repo_path = get_repo_root()
    changes = get_file_changes(repo_path)
    message = message or get_commit_message_from_pending_file(
        get_pending_file_path(repo_path)
    )
    update_pending_changes(repo_path, changes, message)
    return f"\n[green]Updated[/green] {os.path.join(repo_path, 'pending-changes.md')} with current changes."


@cli.command()
@click.option("--keylog", "-k", is_flag=True, default=False, help="Enable logging of key presses to screen")
def review(keylog: bool):
    """Review pending changes and commit message."""
    logger.debug("git workflow tool -> cli -> review")
    output = _review(keylog)
    console.print(output)


def _review(keylog: bool):
    logger.debug("review pending changes")
    repo_path = get_repo_root()
    changes = get_file_changes(repo_path)
    pending_file = get_pending_file_path(repo_path)
    message = get_commit_message_from_pending_file(pending_file)
    update_pending_changes(repo_path, changes, message)

    is_valid, error_message = validate_commit_message(message)
    if not is_valid:
        error_message += "\n\n" + format_validation_error(error_message)

    app_diff_viewer(console, message, changes, error_message, keylog)
    return Markdown(message)


@cli.command()
# @click.option("--message", "-m", help="Commit message")
@click.argument("message", required=False)
def message(message: str):
    """Explicitly set a commit message if unable to use AI to generate it."""
    logger.debug("git workflow tool -> cli -> message")
    output = _message(message)
    console.print(output) if output else None


def _message(message: str):
    logger.debug("generate commit message")

    if not message:
        console.print(
            "[yellow]Note:[/yellow] This feature requires AI assistant integration"
        )
        console.print("Please use the AI assistant to generate your commit message")
        return
    else:
        console.print(f"\n[green]New commit message:[/green] {message}")

    is_valid, error_message = validate_commit_message(message)
    if not is_valid:
        error_message += "\n\n" + format_validation_error(error_message)
        console.print(f"[red]{error_message}[/red]")
        user_confirmation = click.confirm(
            "Are you sure you want to use the invalid commit message?", default=False
        )
        if not user_confirmation:
            console.print("[yellow]Commit message update aborted by user.[/yellow]")
            raise click.Abort()

    _prepare(message)
    return error_message


@cli.command()
@click.option("--amend", is_flag=True, help="Amend the previous commit")
@click.argument("message", required=False)
def commit(message: str, amend: bool):
    """Commit changes with the specified message."""
    logger.debug("git workflow tool -> cli -> commit")
    output = _commit(message, amend)
    console.print(output) if output else None


def _commit(message: str, amend: bool):
    logger.debug("commit changes")

    # Get repo root
    repo_path = get_repo_root()

    # Prepare pending-changes.md
    pending_file = get_pending_file_path(repo_path)
    if not os.path.exists(pending_file):
        _prepare()

    # Validate commit message
    message = message or get_commit_message_from_pending_file(pending_file)
    is_valid, error_message = validate_commit_message(message)
    if not is_valid:
        return "[red]Error:[/red] Commit message is not valid"

    # Confirm commit
    console.print("[green]Commit message:[/green]")
    console.print(f"{message}")
    console.print()
    user_confirmation = click.confirm(
        "Are you sure you want to commit these changes?", default=True
    )
    if not user_confirmation:
        return "[yellow]Commit aborted by user.[/yellow]"

    # Commit changes
    git = Git(repo_path)
    args = ["-m", message]
    if amend:
        args.append("--amend")
    git.commit(*args)
    # repo.index.commit(message, amend=amend)

    # Clean up pending-changes.md
    os.remove(pending_file)

    return "[green]Changes committed successfully![/green]"
