"""Tests for git diff functionality in git_utils."""
import os
from unittest.mock import MagicMock, patch

import git
import pytest

from git_helper.git_utils import FileChange, get_file_diff

@pytest.fixture
def sample_change():
    """Create a sample file change for testing."""
    return FileChange(
        file="test.py",
        status="M",
        status2="S",
        added_lines=10,
        removed_lines=5,
        percent_changed=20.0,
    )

@patch('git_helper.git_utils.git.Repo')
def test_get_file_diff_modified(mock_repo, sample_change):
    """Test getting diff for a modified file."""
    mock_git = MagicMock()
    mock_git.diff.return_value = "sample diff output"
    mock_repo.return_value.git = mock_git
    
    diff = get_file_diff(sample_change)
    assert diff == "sample diff output"
    mock_git.diff.assert_called_once_with('HEAD', sample_change.file, color=True)

@patch('git_helper.git_utils.git.Repo')
def test_get_file_diff_new_file(mock_repo, sample_change, tmp_path):
    """Test getting diff for a new file."""
    # Setup mock to raise GitCommandError for new file
    mock_git = MagicMock()
    mock_git.diff.side_effect = git.exc.GitCommandError('diff', '')
    mock_repo.return_value.git = mock_git
    
    # Create a temporary test file
    test_file = tmp_path / "test.py"
    test_file.write_text("print('test')\n")
    
    with patch('os.path.exists') as mock_exists:
        mock_exists.return_value = True
        with patch('builtins.open', create=True) as mock_open:
            mock_open.return_value.__enter__.return_value.read.return_value = "print('test')"
            
            diff = get_file_diff(sample_change)
            assert diff.startswith("+++ b/")
            assert "print('test')" in diff

@patch('git_helper.git_utils.git.Repo')
def test_get_file_diff_error_handling(mock_repo, sample_change):
    """Test error handling in get_file_diff."""
    # Setup mock to raise GitCommandError
    mock_git = MagicMock()
    mock_git.diff.side_effect = git.exc.GitCommandError('diff', '')
    mock_repo.return_value.git = mock_git
    
    with patch('os.path.exists') as mock_exists:
        mock_exists.return_value = False
        diff = get_file_diff(sample_change)
        assert diff == ""

@patch('git_helper.git_utils.git.Repo')
def test_get_file_diff_with_color(mock_repo, sample_change):
    """Test that diff is requested with color."""
    mock_git = MagicMock()
    mock_git.diff.return_value = "\x1b[32m+new line\x1b[0m"
    mock_repo.return_value.git = mock_git
    
    diff = get_file_diff(sample_change)
    assert diff == "\x1b[32m+new line\x1b[0m"
    mock_git.diff.assert_called_once_with('HEAD', sample_change.file, color=True)
