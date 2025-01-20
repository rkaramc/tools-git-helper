"""Tests for the diff viewer functionality."""
import os
from unittest.mock import MagicMock, patch

import pytest
from rich.console import Console
from rich.layout import Layout
from rich.syntax import Syntax

from git_helper.diff_viewer import DiffViewer
from git_helper.git_utils import FileChange

@pytest.fixture
def console():
    """Create a mock console for testing."""
    return MagicMock(spec=Console)

@pytest.fixture
def sample_changes():
    """Create sample file changes for testing."""
    return [
        FileChange(
            file="test1.py",
            status="M",
            status2="S",
            added_lines=10,
            removed_lines=5,
            percent_changed=20.0,
        ),
        FileChange(
            file="test2.py",
            status="A",
            status2="S",
            added_lines=15,
            removed_lines=0,
            percent_changed=100.0,
        ),
    ]

def test_diff_viewer_initialization(console):
    """Test DiffViewer initialization."""
    viewer = DiffViewer(console)
    assert viewer.current_file_index == 0
    assert viewer.current_change_index == 0
    assert viewer.changes == []

@patch('git_helper.diff_viewer.get_file_diff')
@patch('os.path.getsize')
@patch('os.path.exists')
def test_create_layout_with_changes(mock_exists, mock_getsize, mock_get_diff, console, sample_changes):
    """Test layout creation with sample changes."""
    # Setup mocks
    mock_exists.return_value = True
    mock_getsize.return_value = 1000  # 1KB
    mock_get_diff.return_value = "sample diff content"
    
    viewer = DiffViewer(console)
    layout = viewer.create_layout("test commit message", sample_changes)
    
    assert isinstance(layout, Layout)
    # Check that layout has the expected structure
    assert len(layout.children) == 2
    left_layout = layout.children[0]
    right_layout = layout.children[1]
    assert left_layout.name == "left"
    assert right_layout.name == "right"
    assert viewer.changes == sample_changes

def test_create_layout_without_changes(console):
    """Test layout creation without changes."""
    viewer = DiffViewer(console)
    layout = viewer.create_layout("test commit message", [])
    
    assert isinstance(layout, Layout)
    assert viewer.changes == []

def test_file_navigation(console, sample_changes):
    """Test file navigation functionality."""
    viewer = DiffViewer(console)
    viewer.changes = sample_changes
    
    # Test next file
    assert viewer.current_file_index == 0
    assert viewer.next_file() is True
    assert viewer.current_file_index == 1
    assert viewer.next_file() is False  # At end
    assert viewer.current_file_index == 1
    
    # Test previous file
    assert viewer.prev_file() is True
    assert viewer.current_file_index == 0
    assert viewer.prev_file() is False  # At start
    assert viewer.current_file_index == 0

@patch('git_helper.diff_viewer.get_file_diff')
@patch('os.path.getsize')
@patch('os.path.exists')
def test_get_current_diff(mock_exists, mock_getsize, mock_get_diff, console, sample_changes):
    """Test diff content retrieval."""
    mock_exists.return_value = True
    mock_getsize.return_value = 1000  # 1KB
    mock_get_diff.return_value = "sample diff content"
    
    viewer = DiffViewer(console)
    viewer.changes = sample_changes
    
    diff_content = viewer._get_current_diff()
    assert isinstance(diff_content, Syntax)
    mock_get_diff.assert_called_once()

@patch('os.path.getsize')
@patch('os.path.exists')
def test_large_file_handling(mock_exists, mock_getsize, console, sample_changes):
    """Test handling of large files."""
    mock_exists.return_value = True
    mock_getsize.return_value = 3 * 1024 * 1024  # 3MB
    
    viewer = DiffViewer(console)
    viewer.changes = sample_changes
    
    diff_content = viewer._get_current_diff()
    assert isinstance(diff_content, Syntax)
    assert "File too large" in diff_content.code

@patch('git_helper.diff_viewer.get_file_diff')
def test_parse_diff_hunks(mock_get_diff, console):
    """Test parsing of diff content into hunks."""
    diff_content = (
        "diff --git a/file.py b/file.py\n"
        "@@ -1,3 +1,4 @@\n"
        " def test():\n"
        "+    print('test')\n"
        "     return True\n"
        "@@ -10,2 +11,3 @@\n"
        " def another():\n"
        "+    print('another')\n"
    )
    
    viewer = DiffViewer(console)
    hunks = viewer._parse_diff_hunks(diff_content)
    
    assert len(hunks) == 2
    assert hunks[0].start_line == 1
    assert hunks[1].start_line == 10
    assert "print('test')" in hunks[0].content
    assert "print('another')" in hunks[1].content

@patch('git_helper.diff_viewer.get_file_diff')
def test_change_navigation(mock_get_diff, console, sample_changes):
    """Test navigation between changes in a file."""
    diff_content = (
        "diff --git a/file.py b/file.py\n"
        "@@ -1,3 +1,4 @@\n"
        " def test():\n"
        "+    print('test')\n"
        "@@ -10,2 +11,3 @@\n"
        " def another():\n"
        "+    print('another')\n"
    )
    mock_get_diff.return_value = diff_content
    
    viewer = DiffViewer(console)
    viewer.changes = sample_changes
    
    # Initial state
    assert viewer.current_change_index == 0
    
    # Move to next change
    assert viewer.next_change() is True
    assert viewer.current_change_index == 1
    
    # Try to move past last change
    assert viewer.next_change() is False
    assert viewer.current_change_index == 1
    
    # Move back
    assert viewer.prev_change() is True
    assert viewer.current_change_index == 0
    
    # Try to move before first change
    assert viewer.prev_change() is False
    assert viewer.current_change_index == 0
