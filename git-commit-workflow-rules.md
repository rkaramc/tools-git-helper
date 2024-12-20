# Git Commit Workflow Rules

## Workflow Steps:
1. USER requests Cascade to handle the commit process.
2. Cascade runs `.git/git-workflow.bat` to generate the base `pending-changes.md` file.
3. Cascade reviews `pending-changes.md`, git status, and git diff to create the commit message and file change descriptions.
4. Cascade edits `pending-changes.md` to insert the generated details.
5. Cascade prompts the USER to review the commit message and asks for permission to commit.
6. USER reviews the changes; if approved, Cascade commits the changes and clears `pending-changes.md`.

## Commit Message Generation:
- Cascade will generate concise commit messages based on the changes detected.
- Descriptions for each modified file will be automatically created.

## Pending Changes Management:
- The `pending-changes.md` file will be populated automatically with the current changes.
- The file will include a table with details such as file name, status, added/removed lines, percentage changed, and descriptions.
- The file will be removed after committing the changes to the repository.

## Error Handling:
- Cascade will validate the commit message format and warn if unrelated changes are detected.
- Clear prompts will be provided for each step to minimize confusion.

## Template Storage:
- Workflow templates will be stored in the `.git` directory to keep the project directory clean.
