# Git Helper Tool

[![built with Codeium/Windsurf](https://codeium.com/badges/main)](https://codeium.com/windsurf)

Welcome to the Git Helper Tool!

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
   uv pip install git+https://github.com/rkaramc/tools-git-helper.git
   ```

2. Add the folder [.gw-state/] to your `.git/info/exclude` file (or to the global git ignore file) to prevent it from being tracked by git. This folder is temporary and holds the `pending-changes.md` file during the commit workflow.
   - NOTE: Adding this folder to `.gitignore` may prevent your AI assistant from accessing it. (e.g. Windsurf)

3. If you will be using an AI assistant to generate the commit messages, the `ai-rules.md` file contains sample rules for the assistant. Adapt the rules to your needs and add them to your AI assistant's global rules.

## Usage

You can use the tool by running the following commands.

```bash
# Set a manual commit message
gw-commit message --message "fix: some changes"    # Set a draft commit message provided by the user
                                                   # OR edit the file pending-changes.md in an editor
                                                   # OR request your AI assistant to generate a draft commit message 
                                                   #    and update the file pending-changes.md directly

# Review and edit pending-changes.md
gw-commit review     # Shows the pending changes and draft commit message for review, in a rich terminal UI

# Commit changes
gw-commit commit     # Commits the changes to the repository, with the commit message provided by the user
```

## Features
- Core git workflow automation functionality
- Command-line interface with key commands:
  - `gw-commit` with sub-commands:
    - `message`: Set draft commit message manually
    - `review`: Review pending changes and commit message
    - `commit`: Commit changes (optionally with `--amend` to amend previous commit; with `--message` for manual commit message)


### Technical Implementation
- Using `click` for CLI interface
- Rich text formatting with `rich` library
- Git operations through `gitpython` and subprocess
- `uv` package manager for dependency management
- Organized project structure with src layout

## License

MIT
