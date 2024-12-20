#!/usr/bin/env python3
import os
import subprocess
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, NamedTuple, Optional, Tuple

class FileChange(NamedTuple):
    file: str
    status: str
    added_lines: int
    removed_lines: int
    percent_changed: float
    description: str = ""

def run_git_command(args: List[str], cwd: str) -> Tuple[str, str, int]:
    """Run a git command and return stdout, stderr, and return code."""
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
    
    # Get status of files
    stdout, stderr, return_code = run_git_command(["status", "--porcelain"], repo_path)
    if return_code != 0:
        print(f"Error getting file status: {stderr}")
        return changes

    for line in stdout.split('\n'):
        if not line:
            continue

        status = line[:2]
        file = line[3:].strip()
        
        # Skip .git directory and pending-changes.md
        if file.startswith('.git/') or file == 'pending-changes.md':
            continue

        # Get diff statistics
        if status[1] != 'D':  # Skip deleted files
            diff_stats, _, _ = run_git_command(
                ["diff", "--numstat", file],
                repo_path
            )
            
            if diff_stats:
                added, removed, _ = diff_stats.split('\t')
                try:
                    added_lines = int(added)
                    removed_lines = int(removed)
                    
                    # Calculate percentage changed
                    if status[1] != 'A':  # Not a new file
                        file_content, _, _ = run_git_command(
                            ["show", f"HEAD:{file}"],
                            repo_path
                        )
                        total_lines = len(file_content.split('\n'))
                        percent_changed = ((added_lines + removed_lines) / total_lines * 100) if total_lines > 0 else 100
                    else:
                        percent_changed = 100  # New file
                        
                    changes.append(FileChange(
                        file=file,
                        status=status.strip(),
                        added_lines=added_lines,
                        removed_lines=removed_lines,
                        percent_changed=percent_changed
                    ))

                except ValueError:
                    continue  # Skip binary files

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

type: 

- 

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
    
if __name__ == "__main__":
    repo_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    update_pending_changes(repo_path)
    print("\nUpdated pending-changes.md with current changes.")
