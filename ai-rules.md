# AI Assistant Rules

## Communication Style
- Be concise and direct, avoid fluff
- Focus on technical accuracy
- No apologies or excessive politeness
- Use markdown formatting
- Provide clear, actionable responses

## Development Practices
- Implement changes incrementally
- Follow functional programming principles
- Use proper error handling and validation
- Focus on security and performance

## What Not To Do
- Don't mix concerns in single files
- Don't make undocumented assumptions
- Don't skip architectural decisions
- Don't use imperative patterns
- Don't provide ambiguous solutions

## Code Management
- Organize code logically with separate concerns
- Write comprehensive tests
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
- Descriptive, focused commit messages
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
2. Cascade runs `.git/git-workflow.bat` to generate the base `pending-changes.md` file.
3. Cascade reviews `pending-changes.md` to create the commit message and file change descriptions.
4. Cascade edits `pending-changes.md` to insert the generated message and descriptions.
5. Cascade prompts the USER to review the commit message and asks for permission to commit.
6. USER reviews the changes
7. USER requests Cascade to commit
8. Cascade commits the changes and clears `pending-changes.md`.

### Commit Message Generation:
- Cascade will generate concise commit messages based on the changes detected.
- Descriptions for each modified file will be automatically created.

### Pending Changes Management:
- The `pending-changes.md` file will be populated automatically with the current changes.
- The file will include a table with details such as file name, status, added/removed lines, percentage changed, and descriptions.
- The file will be removed after committing the changes to the repository.

### Error Handling:
- Cascade will validate the commit message format and warn if unrelated changes are detected.
- Clear prompts will be provided for each step to minimize confusion.

### Template Storage:
- Workflow templates will be stored in the `.git` directory to keep the project directory clean.
