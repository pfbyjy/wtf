import pytest
from pathlib import Path
import tempfile
import os
from wtf.history import History
import json
from datetime import datetime, timedelta

@pytest.fixture
def temp_history():
    """Create a temporary history directory and file"""
    with tempfile.TemporaryDirectory() as tmp_dir:
        old_home = os.environ.get('HOME')
        os.environ['HOME'] = tmp_dir
        yield
        if old_home:
            os.environ['HOME'] = old_home

def test_history_creation(temp_history):
    """Test that history file is created"""
    history = History()
    assert history.history_file.parent.exists()

def test_history_add(temp_history):
    """Test adding entries to history"""
    history = History()
    history.add("test prompt", "test command", metadata={"provider": "test"})
    
    entries = history.load()
    assert len(entries) == 1
    assert entries[0]['prompt'] == "test prompt"
    assert entries[0]['command'] == "test command"
    assert entries[0]['metadata']['provider'] == "test"

def test_history_limit(temp_history):
    """Test that history is limited to 1000 entries"""
    history = History()
    for i in range(1100):
        history.add(f"prompt {i}", f"command {i}")
    
    entries = history.load()
    assert len(entries) == 1000
    assert entries[-1]['prompt'] == "prompt 1099" 

def test_history_empty(temp_history):
    """Test handling of empty history"""
    history = History()
    assert history.load() == []
    history.show()  # Should not raise error

def test_history_invalid_json(temp_history):
    """Test handling of corrupted history file"""
    history = History()
    # Write invalid JSON
    history.history_file.write_text("invalid json")
    
    with pytest.raises(json.JSONDecodeError):
        history.load()

def test_history_metadata(temp_history):
    """Test history metadata handling"""
    history = History()
    metadata = {
        "provider": "test",
        "model": "test-model",
        "latency": 1.23,
        "extra": "data"
    }
    history.add("prompt", "command", metadata=metadata)
    
    entries = history.load()
    assert entries[0]['metadata'] == metadata

def test_history_time_formatting(temp_history):
    """Test time formatting in history"""
    history = History()
    
    # Test different time deltas
    now = datetime.now()
    test_cases = [
        (now, "just now"),
        (now - timedelta(minutes=30), "30m ago"),
        (now - timedelta(hours=2), "2h ago"),
        (now - timedelta(days=1), "yesterday"),
        (now - timedelta(days=3), "3d ago"),
    ]
    
    for dt, expected in test_cases:
        assert history._format_time(dt) == expected
    
    # Test old date formatting separately
    old_date = now - timedelta(days=10)
    assert history._format_time(old_date) == old_date.strftime("%Y-%m-%d")

def test_history_success_flag(temp_history):
    """Test history success flag handling"""
    history = History()
    
    # Test successful command
    history.add("good prompt", "good command", success=True)
    # Test failed command
    history.add("bad prompt", "bad command", success=False)
    
    entries = history.load()
    assert entries[0]['success'] is True
    assert entries[1]['success'] is False 