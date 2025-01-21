"""File handling utilities."""

import datetime
import os
from typing import List

from git.cmd import Git

from .formatters import format_markdown_table
from .git_utils import get_file_changes
from .models import FileChange


DRAFT_MESSAGE = """type: concise description of changes

[Optional: detailed explanation for complex changes
- Major changes made
- Rationale for changes
- Impact of changes
]
"""


def update_pending_changes(
    repo_path: str, changes: List[FileChange], message: str = None
) -> None:
    """Update pending-changes.md with current changes."""
    changes = get_file_changes(repo_path)

    current_time = datetime.datetime.now().strftime("%Y-%m-%d")

    diff_output = ""
    if len(changes):
        # Get git diff for all changed files
        for change in changes:
            if os.path.exists(change.file):
                result = Git(repo_path).diff("--no-color", "HEAD", change.file)
                diff_output += f"\n---\n\n### {change.file}\n```diff\n{result}\n```\n"

    content_message = message or DRAFT_MESSAGE
    content = f"""# Pending Changes ({current_time})

## Draft Commit Message

{content_message}

## Modified Files

{format_markdown_table(changes)}

W - Working Dir | S - Staged | ? - New | A - Added | M - Modified | D - Deleted | R - Renamed

!!!WARNING!!! Please update the commit message before committing!

!!!WARNING!!! Only staged files will be commited. Please stage changes you wish to commit.

## Detailed Changes
{diff_output}
"""

    with open(get_pending_file_path(repo_path), "w", encoding="utf-8") as f:
        f.write(content)

    return


def get_commit_message_from_pending_file(pending_file: str) -> str:
    try:
        with open(pending_file, "r", encoding="utf-8") as f:
            content = f.read()
        start = content.find("## Draft Commit Message") + 24
        end = content.find("## Modified Files")
        return content[start:end].strip()
    except FileNotFoundError:
        return ""


def set_commit_message_to_pending_file(pending_file: str, message: str) -> None:
    new_content = None
    with open(pending_file, "r", encoding="utf-8") as f:
        content = f.read()
        start = content.find("## Draft Commit Message") + 24
        end = content.find("## Modified Files")
        new_content = content[:start] + "\n" + message + "\n\n" + content[end:]
    with open(pending_file, "w", encoding="utf-8") as f:
        f.write(new_content)


def get_pending_file_path(repo_path: str) -> str:
    state_dir = os.path.join(repo_path, ".gw-state")
    if not os.path.exists(state_dir):
        os.makedirs(state_dir)

    return os.path.join(state_dir, "pending-changes.md")
