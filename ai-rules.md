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

# Git Commit Workflow Rules for AI Copilots/Assistants

## Workflow Steps:
1. USER requests Cascade to generate the commit message.
2. Cascade reviews `pending-changes.md` and updates the commit message and file change descriptions.
    - The `pending-changes.md` file includes a draft commit message, a list of changed files, and the changes in each file in `diff` format.
    - Cascade will generate a concise commit message for the full commit.
    - Cascade will generate a concise change description for each file, based on the changes detected.
    - Cascade will update the `pending-changes.md` file with the generated commit message and change descriptions.
3. Cascade prompts the USER to review the commit message, and to commit using `gw-commit commit`.
