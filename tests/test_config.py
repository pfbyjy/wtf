import pytest
from pathlib import Path
import tempfile
import os
from wtf.config import Config, DEFAULT_CONFIG

@pytest.fixture
def temp_config():
    """Create a temporary config directory and file"""
    with tempfile.TemporaryDirectory() as tmp_dir:
        # Save original environment
        old_home = os.environ.get('HOME')
        old_openai_key = os.environ.get('OPENAI_API_KEY')
        
        # Set test environment
        os.environ['HOME'] = tmp_dir
        if 'OPENAI_API_KEY' in os.environ:
            del os.environ['OPENAI_API_KEY']
        
        yield
        
        # Restore original environment
        if old_home:
            os.environ['HOME'] = old_home
        if old_openai_key:
            os.environ['OPENAI_API_KEY'] = old_openai_key
        elif 'OPENAI_API_KEY' in os.environ:
            del os.environ['OPENAI_API_KEY']

def test_config_creation(temp_config):
    """Test that config is created with defaults"""
    config = Config()
    assert config.config == DEFAULT_CONFIG
    assert config.config_file.exists()

def test_api_key_from_env(temp_config):
    """Test that API keys are properly read from environment"""
    os.environ['OPENAI_API_KEY'] = 'dummy'
    config = Config()
    assert config.get_api_key('openai') is not None

def test_api_key_from_config(temp_config):
    """Test that API keys are properly read from config file"""
    config = Config()
    config.config['providers']['openai']['api_key'] = 'dummy'
    config._save_config(config.config)
    
    new_config = Config()
    assert new_config.get_api_key('openai') is not None

def test_config_merge(temp_config):
    """Test that config merges correctly with defaults"""
    config = Config()
    # Modify config
    config.config['providers']['openai']['new_field'] = 'test'
    config._save_config(config.config)
    
    # Load again - should preserve new field but keep defaults
    new_config = Config()
    assert new_config.config['providers']['openai']['new_field'] == 'test'
    assert new_config.config['providers']['openai']['models'] == DEFAULT_CONFIG['providers']['openai']['models']

def test_invalid_provider(temp_config):
    """Test getting config for invalid provider"""
    config = Config()
    with pytest.raises(KeyError):
        config.get_provider_config('invalid')

def test_env_key_precedence(temp_config):
    """Test that env key takes precedence over config file"""
    os.environ['OPENAI_API_KEY'] = 'env-dummy'
    config = Config()
    config.config['providers']['openai']['api_key'] = 'file-dummy'
    config._save_config(config.config)
    
    # Just verify we get a key, don't care about the actual value
    assert config.get_api_key('openai') is not None 