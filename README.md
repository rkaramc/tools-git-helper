# Git Workflow Tool

Welcome to the Git Workflow Tool!

Do you find yourself struggling to come up with a clear commit message for your changes? Do you need a better way to review changes before committing? Have you made so many changes at once that you can't keep track of them all?

This tool will help you manage your commits better by providing a structured approach to reviewing changes and drafting commit messages. It currently has the following features: 
1. Helps you review changes before committing.
2. Helps you create clear commit messages, optionally powered by AI.
3. Validate your commit messages to ensure they follow the Conventional Commits specification.

We've included example rules for AI helpers. These show how to use this tool with AI to make better commit messages.

One of the most popular commit message conventions is [Conventional Commits](https://www.conventionalcommits.org/en/v1.0.0-beta.2/). Eventually, this tool will validate your commit messages to ensure they follow the Conventional Commits specification.

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

Remember to add [pending-changes.md] to your `.git/info/exclude` file to prevent it from being tracked in the repository, as it is used as a temporary scratchpad during the commit workflow.
   - NOTE: Adding this file to `.gitignore` may prevent your AI copilot from accessing it. (e.g. Windsurf)

## Usage

You can use the tool by running the following commands.

```bash
# Generate pending changes file
gw-commit prepare    # Scans for changes and prepares a list of changes for review

# Set a manual commit message
gw-commit message --message "fix: some changes"    # Set a draft commit message provided by the user
                                                   # OR edit the file pending-changes.md in an editor
                                                   # OR request your AI copilot to generate a draft commit message 
                                                   #    and update the file pending-changes.md directly

# Review and edit pending-changes.md
gw-commit review     # Shows the pending changes and draft commit message for review

# Commit changes
gw-commit commit     # Commits the changes to the repository, with the commit message provided by the user
```

## Features
- Core git workflow automation functionality
- Command-line interface with key commands:
  - `gw-commit` with sub-commands:
    - `prepare`: Generate pending changes file
    - `message`: Set commit message manually or use an AI copilot to generate it
    - `review`: Review pending changes and commit message
    - `commit`: Commit changes (optionally with `--amend` to amend previous commit; with '--message' for manual commit message)


### Technical Implementation
- Using `click` for CLI interface
- Rich text formatting with `rich` library
- Git operations through `gitpython` and subprocess
- `uv` package manager for dependency management
- Organized project structure with src layout

## License

MIT
