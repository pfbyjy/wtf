import pytest
from click.testing import CliRunner
from wtf.cli import cli
import os

@pytest.fixture
def runner():
    return CliRunner()

def test_cli_help(runner):
    """Test CLI help output"""
    result = runner.invoke(cli, ['--help'])
    assert result.exit_code == 0
    assert 'Convert natural language to shell commands' in result.output

def test_cli_no_command(runner):
    """Test CLI with no command"""
    result = runner.invoke(cli)
    assert result.exit_code != 0
    assert 'Please provide a command description' in result.output

def test_cli_show_config(runner):
    """Test --show-config output"""
    result = runner.invoke(cli, ['--show-config'])
    assert result.exit_code == 0
    assert 'WTF Configuration' in result.output
    assert 'Openai Provider' in result.output
    assert 'Anthropic Provider' in result.output

@pytest.mark.integration
def test_cli_command_generation(runner):
    """Test command generation (requires API key)"""
    if not os.getenv('OPENAI_API_KEY'):
        pytest.skip("No OpenAI API key available")
    
    result = runner.invoke(cli, ['list', 'files'])
    assert result.exit_code == 0
    assert len(result.output.strip()) > 0
    assert '(copied to clipboard)' in result.stderr

def test_cli_history(runner):
    """Test history command"""
    result = runner.invoke(cli, ['--history'])
    assert result.exit_code == 0
    assert 'Command History' in result.output 