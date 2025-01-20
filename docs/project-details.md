## Project: Git Helper Tool

### Core Purpose
- Helps manage git commits with a structured approach
- Assists in reviewing changes and drafting commit messages
- Validates commit messages against Conventional Commits specification

### Key Commands
- `gw-commit prepare`: Generate pending changes file
- `gw-commit message`: Set commit message (manual or AI-assisted)
- `gw-commit review`: Review changes in terminal UI
- `gw-commit commit`: Commit changes to repository

### Important Files
- `pending-changes.md`: Temporary file for tracking changes (should be in .git/info/exclude)
- Uses Conventional Commits format for messages

### Technical Stack
- Python 3.12+
- UV package manager
- Dependencies: click, rich, gitpython
- Source layout project structure
