# Git Workflow Tool

A tool for managing git commits with structured workflows.

## Prerequisites

1. Python 3.12 or higher
2. UV package manager
3. Git initialized in the project

## Installation

1. Install the tool:
   ```bash
   uv pip install git+https://github.com/rkaramc/git-workflow-tool.git
   ```

2. Add the workflow rules `ai-rules.md` (or variant) to your AI copilot. 
   - The `git-commit-workflow` section contains the rules for generating commit messages.

3. Add `pending-changes.md` to your `.git/info/exclude` file.
   - This file is used as a scratchpad for tracking changes during git commit workflow operations.
   - Adding this file to `.git/info/exclude` will prevent it from being committed to the repository.
   - NOTE: Adding this file to `.gitignore` may prevent your AI copilot from accessing it. (e.g. Windsurf)

## Usage

```bash
# Generate pending changes file
gw-commit prepare

# Use your copilot AI to generate commit message
#    (See ai-rules.md and docs/git-commit-workflow-rules.md for details)
gw-commit message

# Review and edit pending-changes.md
gw-commit review

# Commit changes
gw-commit commit
```

## Features
- Core git workflow automation functionality
    - Command-line interface with key commands:
    - `gw-commit` with sub-commands:
        - `prepare`: Generate pending changes file
        - `message`: Use Cascade AI to generate commit message, or set manually
        - `review`: Review pending changes and commit message
        - `commit`: Commit changes (optionally with `--amend` to amend previous commit; with '--message' for manual commit message)


## Development

1. Clone the repository
2. Install development dependencies:
   ```bash
   uv pip install -e ".[dev]"
   ```

### Technical Implementation
- Using `click` for CLI interface
- Rich text formatting with `rich` library
- Git operations through `gitpython` and subprocess
- `uv` package manager for dependency management
- Organized project structure with src layout

## Contributing

1. Fork the repository
2. Create your feature branch
3. Submit a pull request

## License

MIT
