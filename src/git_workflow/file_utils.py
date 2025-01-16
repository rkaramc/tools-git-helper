"""File handling utilities."""

import datetime
import os
from typing import List

from git_workflow.formatters import format_markdown_table
from git_workflow.git_utils import get_diff_output, get_file_changes
from git_workflow.models import FileChange


def update_pending_changes(repo_path: str, changes: List[FileChange]) -> None:
    """Update pending-changes.md with current changes."""
    changes = get_file_changes(repo_path)

    current_time = datetime.datetime.now().strftime("%Y-%m-%d")

    diff_output = ""
    if len(changes):
        # Get git diff for all changed files
        for change in changes:
            result = get_diff_output(repo_path, change.file)
            if result.returncode == 0 and result.stdout:
                diff_output += f"\n### {change.file}\n```diff\n{result.stdout}```\n"

    content = f"""# Pending Changes ({current_time})

## Draft Commit Message

type: concise description of changes

[Optional: detailed explanation for complex changes
- Major changes made
- Rationale for changes
- Impact of changes
]

!!!WARNING!!! Please update the commit message before committing!

## Modified Files

{format_markdown_table(changes)}

Please review the changes and stage the files you wish to include in the commit. Once approved, the staged files will be committed. This file can then be deleted.

## Detailed Changes
{diff_output}
"""

    with open(
        os.path.join(repo_path, "pending-changes.md"), "w", encoding="utf-8"
    ) as f:
        f.write(content)

    return


def get_commit_message_from_pending_file(pending_file: str) -> str:
    with open(pending_file, "r", encoding="utf-8") as f:
        content = f.read()
    start = content.find("## Draft Commit Message") + 24
    end = content.find("## Modified Files")
    return content[start:end].strip()


def set_commit_message_to_pending_file(pending_file: str, message: str) -> None:
    new_content = None
    with open(pending_file, "r", encoding="utf-8") as f:
        content = f.read()
        start = content.find("## Draft Commit Message") + 24
        end = content.find("## Modified Files")
        new_content = content[:start] + "\n" + message + "\n\n" + content[end:]
    with open(pending_file, "w", encoding="utf-8") as f:
        f.write(new_content)
