# /// script
# requires-python = ">=3.12"
# dependencies = []
# ///

import os
import subprocess
from datetime import datetime
from typing import List, NamedTuple, Tuple

class FileChange(NamedTuple):
    file: str
    status: str
    added_lines: int
    removed_lines: int
    percent_changed: float
    description: str = ""

def run_git_command(args: List[str], cwd: str) -> Tuple[str, str, int]:
    """Run a git command and return stdout, stderr, and return code."""
    print(f"Running git command: {' '.join(args)}")
    process = subprocess.Popen(
        ["git"] + args,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        cwd=cwd,
        text=True
    )
    stdout, stderr = process.communicate()
    return stdout.strip(), stderr.strip(), process.returncode

def get_file_changes(repo_path: str) -> List[FileChange]:
    """Get list of changed files with detailed statistics."""
    changes = []
    stats_dict = {}

    # Get diff stats for all modified, unstaged files at once
    diff_stats, _, _ = run_git_command(["diff", "--numstat"], repo_path)
    for line in diff_stats.split('\n'):
        if line:
            added, removed, file = line.split('\t')
            stats_dict[file] = (int(added), int(removed))

    # Get diff stats for all modified, staged files at once
    diff_stats, _, _ = run_git_command(["diff", "--numstat", "--cached"], repo_path)
    for line in diff_stats.split('\n'):
        if line:
            added, removed, file = line.split('\t')
            if file in stats_dict:
                stats_dict[file] = (
                    stats_dict[file][0] + int(added),
                    stats_dict[file][1] + int(removed)
                )
            else:
                stats_dict[file] = (int(added), int(removed))

    # Get status of files
    stdout, stderr, return_code = run_git_command(["status", "--porcelain"], repo_path)
    if return_code != 0:
        print(f"Error getting file status: {stderr}")
        return changes

    for line in stdout.split('\n'):
        if not line:
            continue

        status = line[:2]
        file = line[2:].strip()
        
        # Skip .git directory and pending-changes.md
        if file.startswith('.git/') or file == 'pending-changes.md':
            continue

        # Get diff statistics from the pre-computed stats
        if file in stats_dict:
            added, removed = stats_dict[file]
        else:
            added, removed = 0, 0

        # Calculate percentage changed
        total_lines = added + removed
        percent_changed = (total_lines / max(1, total_lines)) * 100
    
        # Get diff statistics
        if 'D' in status:  # For deleted files, count all lines as removed
            changes.append(FileChange(file, status, 0, removed, 100.0, "File deleted"))
        else:
            if added > 0 or removed > 0:
                # Get total lines in the file for percentage calculation
                # Check both status characters - first char is staging status, second is working tree status
                is_new_file = 'A' in status  # File is new if either staged or unstaged status is 'A'
                if not is_new_file:
                    file_content, _, _ = run_git_command(
                        ["show", f"HEAD:{file}"],
                        repo_path
                    )
                    total_lines = len(file_content.split('\n')) if file_content else 0
                    percent = round((added + removed) / total_lines * 100, 2) if total_lines > 0 else 100
                else:
                    percent = 100  # New file
                
                changes.append(FileChange(
                    file=file,
                    status=status,
                    added_lines=added,
                    removed_lines=removed,
                    percent_changed=percent
                ))

    return changes

def format_markdown_table(changes: List[FileChange]) -> str:
    """Format changes into a markdown table with consistent column widths."""
    if not changes:
        return "No changes detected."

    # Define column headers and widths
    headers = ["File", "Status", "Added", "Removed", "% Changed", "Description"]
    rows = [[
        change.file,
        change.status,
        str(change.added_lines),
        str(change.removed_lines),
        f"{change.percent_changed:.1f}%",
        change.description
    ] for change in changes]
    
    # Calculate column widths
    widths = [len(h) for h in headers]
    for row in rows:
        for i, cell in enumerate(row):
            widths[i] = max(widths[i], len(cell))
    
    # Format table
    sep = "|".join("-" * (w + 2) for w in widths)
    header = "|".join(f" {h:<{w}} " for h, w in zip(headers, widths))
    
    table_rows = [
        "|".join(f" {cell:<{w}} " for cell, w in zip(row, widths))
        for row in rows
    ]
    
    return f"""|{header}|
|{sep}|
""" + "\n".join(f"|{row}|" for row in table_rows)

def update_pending_changes(repo_path: str) -> None:
    """Update pending-changes.md with current changes."""
    changes = get_file_changes(repo_path)
    
    # Group changes by directory to detect unrelated changes
    changes_by_dir = {}
    for change in changes:
        dir_path = os.path.dirname(change.file) or '.'
        if dir_path not in changes_by_dir:
            changes_by_dir[dir_path] = []
        changes_by_dir[dir_path].append(change)
    
    # Warn about unrelated changes
    if len(changes_by_dir) > 1:
        print("\nWarning: Changes detected in multiple directories:")
        for dir_path, dir_changes in changes_by_dir.items():
            print(f"  {dir_path}/")
            for change in dir_changes:
                print(f"    - {change.file}")
        print("\nConsider splitting these changes into separate commits.")
    
    # Generate pending-changes.md content
    if len(changes):
        # Get git diff for all changed files
        diff_output = ""
        for change in changes:
            diff_cmd = ["git", "diff", "--no-color", change.file]
            result = subprocess.run(diff_cmd, capture_output=True, text=True)
            if result.returncode == 0 and result.stdout:
                diff_output += f"\n### {change.file}\n```diff\n{result.stdout}```\n"

        content = f"""# Pending Changes ({datetime.now().strftime('%Y-%m-%d')})

## Draft Commit Message

type: concise description of changes

[Optional: detailed explanation for complex changes
- Major changes made
- Rationale for changes
- Impact of changes
]

## Modified Files

{format_markdown_table(changes)}

Please review the changes and stage the files you want to include in the commit. Once approved, the commit will be made and this file will be cleared.

## Detailed Changes
{diff_output}
"""
        
        # Write to pending-changes.md
        pending_changes_path = os.path.join(repo_path, "pending-changes.md")
        with open(pending_changes_path, "w") as f:
            f.write(content)
            print(content)
    else:
        print("No changes detected.")
    
if __name__ == "__main__":
    print("git-workflow.py")
    print("version: 1.0.0")
    script_path = os.path.abspath(__file__)
    if '.git' in script_path.split(os.path.sep):
        repo_path = os.path.dirname(os.path.dirname(script_path))
    else:
        repo_path = os.path.dirname(script_path)
    update_pending_changes(repo_path)
    print(f"\nUpdated {os.path.join(repo_path, 'pending-changes.md')} with current changes.")
