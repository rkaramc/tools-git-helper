"""Git utility functions."""

import logging
import os
import subprocess
from functools import cache
from typing import List, Tuple

import click
import git
from rich.console import Console

from git_workflow.models import FileChange

console = Console()

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


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
def get_file_changes(repo_path: str, cached_only: bool = False) -> List[FileChange]:
    """Get list of changed files with detailed statistics."""
    changes = []
    stats_dict_unstaged = {}
    stats_dict_staged = {}

    # Get diff stats for all modified, unstaged files at once
    if not cached_only:
        diff_stats, _, _ = run_git_command(["diff", "--numstat"], repo_path)
        for line in diff_stats.split("\n"):
            if line:
                added, removed, file = line.split("\t")
                stats_dict_unstaged[file] = (int(added), int(removed))

    # Get diff stats for all modified, staged files at once
    diff_stats, _, _ = run_git_command(["diff", "--numstat", "--cached"], repo_path)
    for line in diff_stats.split("\n"):
        if line:
            added, removed, file = line.split("\t")
            stats_dict_staged[file] = (int(added), int(removed))

    # Get status of files
    stdout, stderr, return_code = run_git_command(["status", "--porcelain"], repo_path)
    if return_code != 0:
        print(f"Error getting file status: {stderr}")
        return changes

    for line in stdout.split("\n"):
        if not line:
            continue

        status = line[:2]
        file = line[2:].strip().strip('"')

        # Skip .git directory and pending-changes.md
        if file.startswith(".git/") or file == "pending-changes.md":
            logger.info(f"Skipping {file}")
            continue

        if cached_only:
            # If cached_only is True, only check for changes in the cached files
            if file not in stats_dict_staged:
                continue

        # Get diff statistics from the pre-computed stats
        added, removed, status2 = 0, 0, "U"  # untracked
        if file in stats_dict_unstaged:
            added, removed = stats_dict_unstaged[file]
            status2 = "W"  # working copy
        if file in stats_dict_staged:
            added += stats_dict_staged[file][0]
            removed += stats_dict_staged[file][1]
            status2 = "S"  # staging

        # Calculate percentage changed
        total_lines = get_line_count(file, repo_path)

        # Get diff statistics
        if "D" in status:
            # For deleted files, count all lines as removed
            changes.append(
                FileChange(file, status2, status, 0, total_lines, 100.0, "File deleted")
            )
        elif "?" in status or "A" in status:
            # For untracked/added files, count all lines as added
            changes.append(
                FileChange(file, status2, status, total_lines, 0, 100.0, "File added")
            )
        else:
            percent = (
                round(max(added, removed) / total_lines * 100, 2)
                if total_lines > 0
                else 100
            )

            changes.append(
                FileChange(
                    file=file,
                    status2=status2,
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


def validate_commit_message(commit_message: str) -> bool:
    # Add your validation logic here
    # Return True if the commit message is valid, False otherwise
    # Will eventually check for Conventional Commits compliance
    if commit_message.startswith("type: concise description of changes"):
        console.print(
            "[red]Error:[/red] Commit message has not been updated to Conventional Commits format"
        )
        return False
    return True


def get_line_count(file, path):
    with open(os.path.join(path, file), "r", encoding="utf-8") as f:
        return len(f.readlines())
