# Git Workflow Deployment Guide

This guide explains how to deploy the git commit workflow to new projects.

## Prerequisites

1. Python 3.12 or higher
2. UV package manager
3. Git initialized in the project

## Quick Setup

1. Copy the workflow script to your project:
   ```
   <project_root>/.git/git-workflow.py
   ```

2. Add the workflow rules file:
   ```
   <project_root>/ai-rules.md
   ```

3. Add these recommended entries to your `.git/info/exclude`:
   ```
   pending-changes.md
   ```

## Detailed Setup Steps

### 1. Initialize Project Structure

Create the following structure in your project:
```
your-project/
└── .git/
    ├── git-workflow.py        # Core workflow script
    └── info/
        └── exclude            # File to exclude from git commits: add pending-changes.md
```

### 2. Configure Project Scopes

1. Create a `project-scopes.json` in your project root:
```json
{
    "scopes": {
        "core": ["src/core/*", "lib/core/*"],
        "ui": ["src/ui/*", "styles/*"],
        "api": ["src/api/*", "api/*"],
        "docs": ["docs/*", "*.md"],
        "config": ["config/*", "*.json", "*.yaml"],
        "scripts": ["scripts/*", "tools/*"]
    }
}
```

2. Customize the scopes based on your project's structure and components.

### 3. Workflow Integration

1. Set up Git hooks (optional):
   ```bash
   # In .git/hooks/prepare-commit-msg
   #!/bin/sh
   uv run .git/git-workflow.py
   ```

2. Make the hook executable:
   ```bash
   chmod +x .git/hooks/prepare-commit-msg
   ```

## Usage

1. When ready to commit changes:
   ```bash
   uv run .git/git-workflow.py
   ```

2. Review and edit the generated `pending-changes.md`

3. Proceed with the commit when satisfied

## Best Practices

1. **Scope Definition**
   - Define scopes based on logical components
   - Keep scope names short but meaningful
   - Document scope purposes in project documentation

2. **Commit Organization**
   - Group related changes within the same scope
   - Split unrelated changes into separate commits
   - Use conventional commit types consistently

3. **Workflow Customization**
   - Adapt the workflow rules to your project's needs
   - Document any project-specific modifications
   - Keep the workflow documentation up to date

## Troubleshooting

Common issues and solutions:

1. **Script not found**
   - Ensure `git-workflow.py` is in the `.git` directory
   - Check Python and UV installation

2. **Pending changes not showing**
   - Verify git status shows changes
   - Check file permissions
   - Ensure working directory is correct

3. **Scope validation fails**
   - Update project-scopes.json
   - Check file paths match scope patterns
   - Verify JSON syntax

## Maintenance

1. **Regular Updates**
   - Check for workflow script updates
   - Update scope definitions as project evolves
   - Review and refine commit message templates

2. **Team Alignment**
   - Train new team members on workflow
   - Review and update documentation
   - Collect feedback for improvements

## Support

For issues and improvements:
1. Check the improvements tracking file
2. Review workflow rules documentation
3. Submit issues through project tracking system
