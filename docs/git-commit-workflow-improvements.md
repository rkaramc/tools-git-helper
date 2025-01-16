After reviewing our interactions, here are several potential improvements to the git commit workflow:


0. Capabilities
    - [x] Commit message generation, review and commit
    - [ ] Commit history analysis
    - [ ] Custom workflows through plugins
    - [ ] Support for Team Collaboration
    - [ ] Integration with other tools (e.g., Jira, GitHub, Bitbucket)
    - [ ] Integration with code review systems
1. File Change Detection
    - [x] Automate the initial scan of changes and populate pending-changes.md
    - [x] Add line count changes automatically (added/removed lines)
    - [x] Calculate percentage of file changed
    - [x] Optimize performance by batching git diff operations
    - [ ] Highlight staged/unstaged file changes
    - [ ] Add support for binary file changes
    - [ ] Improve handling of renamed files
    - [ ] Add detection for file mode changes
    - [ ] Track file history for moved files
2. Table Formatting
    - [x] Enforce consistent column widths from the start
    - [x] Add automatic table formatting when updating pending-changes.md
    - [x] Use structured template with pre-aligned columns
    - [ ] Add indicator for staged/unstaged changed files
    - [ ] Support for collapsible sections in large commits
    - [ ] Add file grouping by change type
    - [ ] Support for custom column configurations
3. Commit Message Structure
    - [x] Support conventional commit types
    - [x] Basic commit message validation
    - [ ] Add validation for commit message format
    - [ ] Validate scope in commit messages (e.g., type(scope): message)
    - [ ] Add optional footer for breaking changes
    - [ ] Implement commit message templates based on change types
    - [ ] Support for multi-line commit messages with proper formatting
4. Change Grouping
    - [x] Basic change detection and grouping
    - [ ] Define pre-set scopes based on project components/modules
    - [ ] Enforce logical change grouping using pre-set scopes
    - [ ] Warn if unrelated changes are being committed together
    - [ ] Provide option to split changes into separate commits
    - [ ] Add support for commit squashing
    - [ ] "Smart" detection of related changes+commit splitting suggestions
5. Template Management
    - [x] Store workflow script in a maintainable location
    - [x] Implement modular code structure with single responsibility
    - [x] Basic template support
    - [ ] Add template versioning
    - [ ] Include more structured sections (Breaking Changes, Dependencies)
    - [ ] Support custom templates per repository
    - [ ] Template inheritance and overrides
6. User Experience
    - [x] Add clear prompts for each step
    - [x] Show detailed file change statistics
    - [x] Basic command-line interface
    - [x] Add option to amend previous commit
    - [ ] Show version information and installation status
    - [ ] Provide interactive commit message editing with preview and undo/redo
    - [ ] Provide interactive file change preview with colorized diff
    - [ ] Rich terminal UI with navigation
    - [ ] Add support for shell completion in bash/zsh/pwsh/fish
    - [ ] Improve documentation with more usage examples
7. Error Handling
    - [x] Basic error reporting
    - [ ] Add detailed error messages for common git operations
    - [ ] Implement automatic retry for transient failures
    - [ ] Add validation for file encodings
    - [ ] Provide suggestions for resolving merge conflicts
    - [ ] Implement error recovery mechanisms
    - [ ] Add debug logging options
8. Integration Features
    - [x] Basic git integration
    - [ ] Add support for issue tracking links
    - [ ] Integrate with CI/CD status checks
    - [ ] Support for commit signing
    - [ ] Add hooks for custom validation rules
    - [ ] Support for multiple remote repositories
9. Testing and Quality
    - [x] Basic project structure
    - [ ] Unit test suite
    - [ ] Integration tests
    - [ ] Performance benchmarks
    - [ ] Code coverage reporting
    - [ ] Static type checking
    - [ ] Documentation tests
    - [ ] Security audits
10. Developer Experience
    - [ ] github CI/CD configuration
    - [ ] automated publish to pypi
