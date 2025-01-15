# AI Assistant Rules

## What Not To Do
- Don't make undocumented assumptions
- Don't skip architectural decisions
- Don't provide ambiguous solutions

## Communication Style
- Be concise and direct, avoid fluff
- Speak in complete sentences
- Avoid lists if possible
- Focus on technical accuracy
- Provide clear, actionable responses

## Development Practices
- Implement changes incrementally
- Separate concerns in separate files
- Functions should handle a single responsibility

## Code Management
- Document architectural decisions
- Phased development approach
- Focus on maintainability and clarity

## Response Format
1. Acknowledge requirement
2. Clarify ambiguities if any
3. State planned actions
4. Execute changes
5. Summarize changes
6. Document changes with [Git Commit Workflow](#git-commit-workflow)
7. Suggest next steps

## Git Practices
- Conventional commits
- Logical grouping of changes
- Commit message template: 
   ```
   type: concise description of changes

   [Optional: detailed explanation for complex changes
    - Major changes made
    - Rationale for changes
    - Impact of changes]
   ```

## Git Commit Workflow
### Workflow Steps:
1. USER requests Cascade to update the pending-changes.md file.
2. Cascade runs `uv run .git  /git-workflow.py` to generate the base `pending-changes.md` file.
3. Cascade reviews `pending-changes.md` to create the commit message and file change descriptions.
4. Cascade edits `pending-changes.md` to insert the generated message and descriptions.
5. Cascade prompts the USER to review the commit message and asks for permission to commit.
6. USER reviews the changes
7. USER requests Cascade to commit
8. Cascade commits the changes and removes `pending-changes.md`.
