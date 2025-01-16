"""Main entry point for the git-workflow tool"""

import datetime
import logging
import os
import subprocess
from typing import List, NamedTuple, Tuple

import click
import git
from rich import print
from rich.console import Console
from rich.markdown import Markdown
from rich.table import Table

console = Console()

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class FileChange(NamedTuple):
    file: str
    status: str
    added_lines: int
    removed_lines: int
    percent_changed: float
    description: str = ""


def run_git_command(args: List[str], cwd: str) -> Tuple[str, str, int]:
    """Run a git command and return stdout, stderr, and return code."""
    logger.debug(f"Running git command: {' '.join(args)}")
    process = subprocess.Popen(
        ["git"] + args,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        cwd=cwd,
        text=True,
    )
    stdout, stderr = process.communicate()
    return stdout.strip(), stderr.strip(), process.returncode


def get_file_changes(repo_path: str) -> List[FileChange]:
    """Get list of changed files with detailed statistics."""
    changes = []
    stats_dict = {}

    # Get diff stats for all modified, unstaged files at once
    diff_stats, _, _ = run_git_command(["diff", "--numstat"], repo_path)
    for line in diff_stats.split("\n"):
        if line:
            added, removed, file = line.split("\t")
            stats_dict[file] = (int(added), int(removed))

    # Get diff stats for all modified, staged files at once
    diff_stats, _, _ = run_git_command(["diff", "--numstat", "--cached"], repo_path)
    for line in diff_stats.split("\n"):
        if line:
            added, removed, file = line.split("\t")
            if file in stats_dict:
                stats_dict[file] = (
                    stats_dict[file][0] + int(added),
                    stats_dict[file][1] + int(removed),
                )
            else:
                stats_dict[file] = (int(added), int(removed))

    # Get status of files
    stdout, stderr, return_code = run_git_command(["status", "--porcelain"], repo_path)
    if return_code != 0:
        print(f"Error getting file status: {stderr}")
        return changes

    for line in stdout.split("\n"):
        if not line:
            continue

        status = line[:2]
        file = line[2:].strip()

        # Skip .git directory and pending-changes.md
        if file.startswith(".git/") or file == "pending-changes.md":
            continue

        # Get diff statistics from the pre-computed stats
        if file in stats_dict:
            added, removed = stats_dict[file]
        else:
            added, removed = 0, 0

        # Calculate percentage changed
        total_lines = added + removed

        # Get diff statistics
        if "D" in status:  # For deleted files, count all lines as removed
            changes.append(FileChange(file, status, 0, removed, 100.0, "File deleted"))
        else:
            if added > 0 or removed > 0:
                # Get total lines in the file for percentage calculation
                # Check both status characters - first char is staging status, second is working tree status
                is_new_file = (
                    "A" in status
                )  # File is new if either staged or unstaged status is 'A'
                if not is_new_file:
                    file_content, _, _ = run_git_command(
                        ["show", f"HEAD:{file}"], repo_path
                    )
                    total_lines = len(file_content.split("\n")) if file_content else 0
                    percent = (
                        round((added + removed) / total_lines * 100, 2)
                        if total_lines > 0
                        else 100
                    )
                else:
                    percent = 100  # New file

            changes.append(
                FileChange(
                    file=file,
                    status=status,
                    added_lines=added,
                    removed_lines=removed,
                    percent_changed=percent,
                )
            )

    return changes


def get_repo_root() -> str:
    """Find git repository root."""
    try:
        repo = git.Repo(search_parent_directories=True)
        return repo.working_tree_dir
    except git.exc.InvalidGitRepositoryError:
        console.print("[red]Error:[/red] Not in a git repository")
        raise click.Abort()


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
            change.status,
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
            change.status,
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


def update_pending_changes(repo_path: str):
    """Update pending-changes.md with current changes."""
    changes = get_file_changes(repo_path)

    current_time = datetime.datetime.now().strftime("%Y-%m-%d")

    content = f"""# Pending Changes ({current_time})

## Draft Commit Message

type: concise description of changes

[Optional: detailed explanation for complex changes
- Major changes made
- Rationale for changes
- Impact of changes
]

## Modified Files

{format_markdown_table(changes)}
"""

    with open(
        os.path.join(repo_path, "pending-changes.md"), "w", encoding="utf-8"
    ) as f:
        f.write(content)


@click.group()
def cli():
    """Git Workflow Tool - A structured approach to git commits."""
    pass


@cli.command()
def prepare():
    """Generate pending-changes.md with current changes."""
    repo_path = get_repo_root()
    update_pending_changes(repo_path)
    console.print(
        f"\n[green]Updated[/green] {os.path.join(repo_path, 'pending-changes.md')} with current changes."
    )


@cli.command()
def review():
    """Review pending changes in a formatted view."""
    repo_path = get_repo_root()
    changes = get_file_changes(repo_path)

    if not changes:
        console.print("[yellow]No changes detected[/yellow]")
        return

    table = format_rich_table(changes)
    console.print(table)

    pending_file = os.path.join(repo_path, "pending-changes.md")
    if os.path.exists(pending_file):
        with open(pending_file, "r", encoding="utf-8") as f:
            md = Markdown(f.read())
            console.print(md)


@cli.command()
@click.option("--message", "-m", help="Commit message")
def message(message: str):
    """Use Cascade AI to generate commit message."""
    repo_path = get_repo_root()

    if not message:
        console.print(
            "[yellow]Note:[/yellow] This feature requires Cascade AI integration"
        )
        console.print(
            "Please use the Cascade AI assistant to generate your commit message"
        )
        raise click.Abort()

    console.print(f"[green]Commit message:[/green] {message}")

    pending_file = os.path.join(repo_path, "pending-changes.md")
    if os.path.exists(pending_file):
        new_content = None
        with open(pending_file, "r", encoding="utf-8") as f:
            content = f.read()
            start = content.find("## Draft Commit Message") + 21
            end = content.find("## Modified Files")
            new_content = content[:start] + message + content[end:]

        if new_content is not None:
            with open(pending_file, "w", encoding="utf-8") as f:
                f.write(new_content)
                console.print(
                    f"[green]Updated[/green] {pending_file} with commit message"
                )


@cli.command()
@click.option("--message", "-m", help="Commit message")
@click.option("--amend", is_flag=True, help="Amend previous commit")
def commit(message: str, amend: bool):
    """Commit changes with the specified message."""
    repo_path = get_repo_root()

    if not message:
        pending_file = os.path.join(repo_path, "pending-changes.md")
        if not os.path.exists(pending_file):
            prepare()

        if os.path.exists(pending_file):
            with open(pending_file, "r", encoding="utf-8") as f:
                content = f.read()
                # Extract commit message from pending-changes.md
                start = content.find("## Draft Commit Message") + 21
                end = content.find("## Modified Files")
                if start > 0 and end > 0:
                    message = content[start:end].strip()

    if not message:
        console.print("[red]Error:[/red] No commit message provided")
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


if __name__ == "__main__":
    cli()
