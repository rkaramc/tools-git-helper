# Git Workflow Tool

A tool for managing git commits with structured workflows.

## Installation

```bash
uv pip install git+https://github.com/rkaramc/git-workflow-tool.git
```

## Usage

```bash
# Generate pending changes file
gw-commit-prepare

# Review and edit pending-changes.md
gw-commit-review

# Use cascade AI to generate commit message
gw-commit-message

# Commit changes
gw-commit
```

## Features

- Automatic change detection
- Detailed file statistics
- Structured commit messages
- Change grouping support
- Customizable templates

## Development

1. Clone the repository
2. Install development dependencies:
   ```bash
   uv pip install -e ".[dev]"
   ```

## Contributing

1. Fork the repository
2. Create your feature branch
3. Submit a pull request

## License

MIT
