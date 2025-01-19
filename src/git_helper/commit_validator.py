"""Commit message validation using conventional commits specification."""

import re
from typing import Optional, Tuple, Set
from dataclasses import dataclass

@dataclass
class ConventionalCommit:
    """Represents a parsed conventional commit message."""
    type: str
    scope: Optional[str]
    description: str
    body: Optional[str]
    breaking: bool
    footers: list[str]

class CommitValidator:
    """Validates commit messages against the Conventional Commits specification."""
    
    COMMIT_PATTERN = re.compile(
        r"^(?P<type>[a-z]+)"
        r"(?:\((?P<scope>[a-z0-9/-]+)\))?"
        r"(?P<breaking>!)?"
        r": "
        r"(?P<description>(?:(?!^(feat|fix|docs|style|refactor|perf|test|build|ci|chore|revert)(\(|\!|\:)).*(?:\n(?!\n).*)*)?)"
        r"(?:\n\n(?P<body>(?:(?!^(feat|fix|docs|style|refactor|perf|test|build|ci|chore|revert)(\(|\!|\:)).*(?:\n.*)*)?))?"
        r"(?:\n\n(?P<footer>(?:(?!^(feat|fix|docs|style|refactor|perf|test|build|ci|chore|revert)(\(|\!|\:)).*(?:\n.*)*)?))?"
        r"$",
        re.MULTILINE
    )
    
    ALLOWED_TYPES: Set[str] = {
        'feat', 'fix', 'docs', 'style', 'refactor',
        'perf', 'test', 'build', 'ci', 'chore', 'revert'
    }

    @classmethod
    def parse_commit_message(cls, message: str) -> Optional[ConventionalCommit]:
        """
        Parse a commit message into its components.
        
        Args:
            message: The commit message to parse
            
        Returns:
            ConventionalCommit object if valid, None if invalid
        """
        match = cls.COMMIT_PATTERN.match(message)
        if not match:
            return None
            
        groups = match.groupdict()
        return ConventionalCommit(
            type=groups['type'],
            scope=groups['scope'],
            description=groups['description'].strip() if groups['description'] else '',
            body=groups['body'].strip() if groups['body'] else None,
            breaking=bool(groups['breaking']),
            footers=groups['footer'].strip().split('\n') if groups['footer'] else []
        )

def validate_commit_message(message: str) -> Tuple[bool, Optional[str]]:
    """
    Validate a commit message against the Conventional Commits specification.
    
    Args:
        message: The commit message to validate
        
    Returns:
        Tuple of (is_valid: bool, error_message: Optional[str])
        If the message is valid, error_message will be None
    """
    if not message:
        return False, "Commit message cannot be empty"
        
    commit = CommitValidator.parse_commit_message(message)
    if not commit:
        return False, "Invalid commit message format. Expected format: type(scope?): description"
        
    if commit.type not in CommitValidator.ALLOWED_TYPES:
        return False, f"Invalid type '{commit.type}'. Allowed types are: {', '.join(sorted(CommitValidator.ALLOWED_TYPES))}"
        
    if not commit.description:
        return False, "Commit message must include a description"
        
    return True, None

def format_validation_error(error: str) -> str:
    """
    Format a validation error message to be more user-friendly.
    
    Args:
        error: The raw error message
        
    Returns:
        A formatted error message with suggestions if applicable
    """
    # Common error mappings to more user-friendly messages
    error_mappings = {
        "invalid commit message format": 
            "Commit message must follow the format: type(scope?): description\n"
            "Examples:\n"
            "  feat: add new feature\n"
            "  fix(auth): resolve login issue\n"
            "  docs: update README",
        "invalid type": 
            "Type must be one of: feat, fix, docs, style, refactor, perf, test, build, ci, chore, revert",
        "must include a description":
            "Description cannot be empty. Add a clear, concise description of the change."
    }
    
    for key, friendly_message in error_mappings.items():
        if key.lower() in error.lower():
            return friendly_message
            
    return error

def get_commit_type(message: str) -> Optional[str]:
    """
    Extract the type from a conventional commit message.
    
    Args:
        message: The commit message
        
    Returns:
        The commit type if found, None otherwise
    """
    commit = CommitValidator.parse_commit_message(message)
    return commit.type if commit else None
