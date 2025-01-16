"""Command line interface for git workflow."""

import logging
import os

import click
import git
from rich.console import Console
from rich.markdown import Markdown

from git_workflow.file_utils import (
    get_commit_message_from_pending_file,
    set_commit_message_to_pending_file,
    update_pending_changes,
)
from git_workflow.formatters import format_rich_table
from git_workflow.git_utils import get_file_changes, get_repo_root, validate_commit_message

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
    """Review pending changes in a formatted view."""
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
        prepare()

    if os.path.exists(pending_file):
        with open(pending_file, "r", encoding="utf-8") as f:
            content = f.read()
            start = content.find("## Draft Commit Message")
            end = content.find("## Modified Files")
            md = Markdown(content[start:end])
            console.print(md)
    table = format_rich_table(changes)
    console.print(table)


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
        raise click.Abort()

    console.print(f"[green]New commit message:[/green] {message}")

    pending_file = os.path.join(repo_path, "pending-changes.md")
    if not os.path.exists(pending_file):
        prepare()

    if os.path.exists(pending_file):
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
