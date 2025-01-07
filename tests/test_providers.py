import pytest
from wtf.providers import get_provider, OpenAIProvider, AnthropicProvider
import click
import os
from unittest.mock import Mock, patch

def test_get_provider_unknown():
    """Test that unknown provider raises error"""
    with pytest.raises(click.ClickException) as exc:
        get_provider('unknown', {})
    assert 'Unknown provider' in str(exc.value)

def test_get_provider_no_key(monkeypatch):
    """Test that missing API key raises error"""
    # Clear any existing env var
    monkeypatch.delenv('OPENAI_API_KEY', raising=False)
    
    config = {
        'default_provider': 'openai',
        'providers': {
            'openai': {
                'api_key': '',
                'env_key': 'OPENAI_API_KEY',
                'default_model': 'gpt-4o',
                'models': ['gpt-3.5-turbo', 'gpt-4', 'gpt-4o']
            }
        }
    }
    with pytest.raises(click.ClickException) as exc:
        get_provider('openai', config)
    assert 'No API key found' in str(exc.value)

@pytest.mark.integration
def test_openai_provider():
    """Test OpenAI provider (requires API key)"""
    provider = OpenAIProvider(os.getenv('OPENAI_API_KEY'))
    result = provider.get_shell_command('list files', 'gpt-3.5-turbo')
    assert isinstance(result, str)
    assert len(result) > 0

@pytest.mark.integration
def test_anthropic_provider():
    """Test Anthropic provider (requires API key)"""
    provider = AnthropicProvider(os.getenv('ANTHROPIC_API_KEY'))
    result = provider.get_shell_command('list files', 'claude-3-sonnet')
    assert isinstance(result, str)
    assert len(result) > 0 

def test_create_prompt():
    """Test prompt creation"""
    provider = OpenAIProvider("dummy-key")
    prompt = provider.create_prompt("list files")
    assert "list files" in prompt
    assert "shell" in prompt.lower()

@pytest.mark.integration
def test_openai_provider_invalid_key():
    """Test OpenAI provider with invalid key"""
    provider = OpenAIProvider("invalid-key")
    with pytest.raises(Exception):
        provider.get_shell_command('list files', 'gpt-3.5-turbo')

@pytest.mark.integration
def test_anthropic_provider_invalid_key():
    """Test Anthropic provider with invalid key"""
    provider = AnthropicProvider("invalid-key")
    with pytest.raises(Exception):
        provider.get_shell_command('list files', 'claude-3-sonnet')

def test_provider_error_handling():
    """Test error handling in get_provider"""
    config = {
        'providers': {
            'openai': {
                'api_key': 'test',
                'env_key': 'MISSING_KEY',
                'default_model': 'gpt-4o',
                'models': ['gpt-3.5-turbo', 'gpt-4', 'gpt-4o']
            }
        }
    }
    # Should fall back to config key when env var is missing
    provider = get_provider('openai', config)
    assert isinstance(provider, OpenAIProvider)

@patch('wtf.providers.OpenAI')
def test_openai_provider_params(mock_openai_class):
    """Test OpenAI provider parameters"""
    # Create a mock response object with the correct structure
    mock_response = Mock()
    mock_response.choices = [Mock(message=Mock(content="ls"))]
    
    # Set up the mock client
    mock_client = Mock()
    mock_client.chat.completions.create.return_value = mock_response
    mock_openai_class.return_value = mock_client
    
    provider = OpenAIProvider(os.getenv('OPENAI_API_KEY'))
    result = provider.get_shell_command("list files", "gpt-4")
    
    # Verify correct parameters were passed
    assert mock_client.chat.completions.create.call_count == 1
    call_args = mock_client.chat.completions.create.call_args[1]
    assert call_args['model'] == "gpt-4"
    assert call_args['temperature'] == 0.1
    assert len(call_args['messages']) == 2
    assert result == "ls" 