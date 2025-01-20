"""Git utility functions."""

import logging
import os
import re
import subprocess
from functools import cache
from typing import List

import click
import git
from git.cmd import Git
from rich.console import Console

from .models import FileChange

console = Console()

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


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
        # diff_stats, _, _ = run_git_command(["diff", "--numstat"], repo_path)
        diff_stats = Git(repo_path).diff("--numstat")
        for line in diff_stats.split("\n"):
            if line:
                added, removed, file = line.split("\t")
                stats_dict_unstaged[file] = (int(added), int(removed))

    # Get diff stats for all modified, staged files at once
    # diff_stats, _, _ = run_git_command(["diff", "--numstat", "--staged"], repo_path)
    diff_stats = Git(repo_path).diff("--numstat", "--staged")
    for line in diff_stats.split("\n"):
        if line:
            added, removed, file = line.split("\t")
            old_file = ""
            if " => " in file:
                # Parse renamed files
                rename_regex = r"^(.+)\{(.+) => (.+)\}(.*)$"
                match = re.match(rename_regex, file)
                if match:
                    old_file = match.group(1) + match.group(2) + match.group(4)
                    new_file = match.group(1) + match.group(3) + match.group(4)
                    file = new_file
            stats_dict_staged[file] = (int(added), int(removed), old_file)

    # Get status of files
    stdout = Git(repo_path).status("--porcelain")
    for line in stdout.split("\n"):
        if not line:
            continue

        status = line[:2]
        file = line[2:].strip().strip('"')

        # Skip .git directory and pending-changes.md
        if file.startswith(".git/") or file == "pending-changes.md":
            logger.info(f"Skipping {file}")
            continue

        if " -> " in file:
            file = file.split(" -> ")[1]
            old_file = file.split(" -> ")[0]
            change = FileChange(
                file, "", "R", 0, 0, 100.0, f"<<{old_file}>>"
            )
        else:
            change = FileChange(file, "", status, 0, 0, 100.0, "")

        # Get diff statistics from the pre-computed stats
        added_lines = 0
        removed_lines = 0
        status2 = ""
        description = ""

        if file in stats_dict_unstaged:
            added_lines, removed_lines = stats_dict_unstaged[file]
            status2 = "W"  # working copy
        if file in stats_dict_staged:
            added_lines += stats_dict_staged[file][0]
            removed_lines += stats_dict_staged[file][1]
            status2 += "S"  # staging

        # Calculate percentage changed
        total_lines = get_line_count(file, repo_path)

        # Get diff statistics
        if "D" in status:
            # For deleted files, count all lines as removed
            removed_lines = total_lines
            description = "<deleted>"
        elif "?" in status or "A" in status:
            # For untracked/added files, count all lines as added
            added_lines = total_lines
            description = "<<added>>"

        percent_changed = (
            round(max(added_lines, removed_lines) / total_lines * 100, 2)
            if total_lines > 0
            else 100
        )

        # Create a new FileChange instance with all the computed values
        change = FileChange(
            file=file,
            status2=status2,
            status=status,
            added_lines=added_lines,
            removed_lines=removed_lines,
            percent_changed=percent_changed,
            description=description + change.description,
        )
        changes.append(change)

    return changes


def get_diff_output(repo_path: str, file: str) -> str:
    """Get git diff for changed file."""
    diff_cmd = ["git", "diff", "--no-color", "HEAD", file]
    result = subprocess.run(diff_cmd, capture_output=True, text=True)
    result = Git(repo_path).diff("--no-color", "HEAD", file)
    return result


def get_line_count(file, path):
    file_path = os.path.join(path, file)
    if not os.path.exists(file_path):
        return 0
    if os.path.isdir(file_path):
        return 0
    with open(file_path, "r", encoding="utf-8") as f:
        return len(f.readlines())


def get_file_diff(change: FileChange) -> str:
    """Get the diff content for a file."""
    repo = git.Repo(get_repo_root())
    
    try:
        # Get the diff for the file
        diff = repo.git.diff('HEAD', change.file, color=True)
        return diff
    except git.exc.GitCommandError:
        # For new files, show the entire content
        if os.path.exists(change.file):
            with open(change.file, 'r', encoding='utf-8') as f:
                content = f.read()
            return f"+++ b/{change.file}\n" + "\n".join(f"+{line}" for line in content.splitlines())
        return ""
