"""Git utility functions."""

import logging
import subprocess
from functools import cache
from typing import List, Tuple

import click
import git
from rich.console import Console

from .models import FileChange

console = Console()
logger = logging.getLogger(__name__)


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


def get_repo_root() -> str:
    """Find git repository root."""
    try:
        repo = git.Repo(search_parent_directories=True)
        return repo.working_tree_dir
    except git.exc.InvalidGitRepositoryError:
        console.print("[red]Error:[/red] Not in a git repository")
        raise click.Abort()


@cache
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
            percent = 100
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

def get_diff_output(repo_path: str, file: str) -> str:
    """Get git diff for changed file."""
    diff_cmd = ["git", "diff", "--no-color", "HEAD", file]
    result = subprocess.run(diff_cmd, capture_output=True, text=True)
    return result