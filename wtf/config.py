from pathlib import Path
import os
from typing import Dict, Any, Optional
import yaml
import click
import logging

logger = logging.getLogger(__name__)

DEFAULT_CONFIG = {
    "default_provider": "openai",
    "default_model": "gpt-4o",
    "providers": {
        "openai": {
            "api_key": "",
            "default_model": "gpt-4o",
            "models": ["gpt-3.5-turbo", "gpt-4", "gpt-4o"],
            "env_key": "OPENAI_API_KEY"
        },
        "anthropic": {
            "api_key": "",
            "default_model": "claude-3-5-sonnet",
            "models": ["claude-3-sonnet", "claude-3-opus", "claude-3-haiku", "claude-3-5-sonnet", "claude-3-5-haiku", "claude-3-5-opus"],
            "env_key": "ANTHROPIC_API_KEY"
        }
    }
}

class Config:
    def __init__(self):
        self.config_dir = Path.home() / '.config' / 'wtf'
        self.config_file = self.config_dir / 'config.yaml'
        self.config = self._load_config()

    def _merge_configs(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Ensure all default fields exist in the config"""
        result = DEFAULT_CONFIG.copy()
        if config:
            for provider, settings in config.get('providers', {}).items():
                if provider in result['providers']:
                    result['providers'][provider].update(settings)
            if 'default_provider' in config:
                result['default_provider'] = config['default_provider']
            if 'default_model' in config:
                result['default_model'] = config['default_model']
        return result

    def _load_config(self) -> Dict[str, Any]:
        if not self.config_file.exists():
            self.config_dir.mkdir(parents=True, exist_ok=True)
            self._save_config(DEFAULT_CONFIG)
            return DEFAULT_CONFIG
        
        with open(self.config_file, 'r') as f:
            config = yaml.safe_load(f) or {}
        
        # Merge with defaults to ensure all required fields exist
        merged_config = self._merge_configs(config)
        if merged_config != config:
            self._save_config(merged_config)
        return merged_config

    def _save_config(self, config: Dict[str, Any]):
        with open(self.config_file, 'w') as f:
            yaml.dump(config, f)

    def get_provider_config(self, provider: Optional[str] = None) -> Dict[str, Any]:
        provider = provider or self.config['default_provider']
        return self.config['providers'][provider]

    def get_api_key(self, provider: str) -> Optional[str]:
        provider_config = self.config['providers'][provider]
        # First check environment variable
        if env_key := provider_config.get('env_key'):
            api_key = os.getenv(env_key)
            logger.debug(f"Checking env var {env_key}: {'found' if api_key else 'not found'}")  # This goes to log file only
            if api_key:
                return api_key
        # Fall back to config file
        config_key = provider_config.get('api_key')
        logger.debug(f"Checking config file: {'found' if config_key else 'not found'}")  # This goes to log file only
        return config_key 

    def check_first_run(self) -> bool:
        """Check if this is first run and show helpful info"""
        if not self.config_file.exists():
            click.echo("\n🎉 Welcome to WTF! Let's get you set up.\n")
            click.echo("You'll need an API key from OpenAI or Anthropic.")
            click.echo("\nTo set up OpenAI:")
            click.echo("1. Get a key from https://platform.openai.com/api-keys")
            click.echo("2. Run: wtf-config set-key openai sk-...")
            click.echo("\nOr for Anthropic:")
            click.echo("1. Get a key from https://console.anthropic.com/settings/keys")
            click.echo("2. Run: wtf-config set-key anthropic sk-...\n")
            return True
        return False 