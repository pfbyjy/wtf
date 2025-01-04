from typing import Dict, Any, Optional
import click
from openai import OpenAI
from anthropic import Anthropic
from wtf.config import Config
import os
import logging

logger = logging.getLogger('wtf')

class AIProvider:
    def create_prompt(self, command: str) -> str:
        return f"""Convert this natural language command into a shell pipeline. 
Respond with only the shell command, no explanations or markdown.
The command should work on Unix-like systems.

Natural language: {command}"""

class OpenAIProvider(AIProvider):
    def __init__(self, api_key: str):
        self.client = OpenAI(api_key=api_key)

    def get_shell_command(self, text: str, model: str) -> str:
        response = self.client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "You are a helpful assistant that converts natural language into shell commands. Provide only the command, no explanations."},
                {"role": "user", "content": self.create_prompt(text)}
            ],
            temperature=0.1
        )
        return response.choices[0].message.content.strip()

class AnthropicProvider(AIProvider):
    def __init__(self, api_key: str):
        self.client = Anthropic(api_key=api_key)

    def get_shell_command(self, text: str, model: str) -> str:
        response = self.client.messages.create(
            model=model,
            max_tokens=100,
            messages=[{
                "role": "user",
                "content": self.create_prompt(text)
            }],
            system="You are a helpful assistant that converts natural language into shell commands. Provide only the command, no explanations."
        )
        return response.content[0].text.strip()

def get_provider(name: str, config: Dict[str, Any]) -> AIProvider:
    providers = {
        "openai": OpenAIProvider,
        "anthropic": AnthropicProvider
    }
    
    provider_class = providers.get(name)
    if not provider_class:
        available = ", ".join(providers.keys())
        raise click.ClickException(f"Unknown provider '{name}'. Available providers: {available}")
    
    config_obj = Config()
    api_key = config_obj.get_api_key(name)
    if not api_key:
        env_key = config_obj.config['providers'][name]['env_key']
        raise click.ClickException(
            f"\nNo API key found for {name}. You can set it by either:\n"
            f"1. Setting environment variable: export {env_key}=sk-...\n"
            f"2. Using config command: wtf-config set-key {name} sk-...\n"
        )
    
    return provider_class(api_key) 

def get_api_key(self, provider: str) -> Optional[str]:
    provider_config = self.config['providers'][provider]
    # First check environment variable
    if env_key := provider_config.get('env_key'):
        api_key = os.getenv(env_key)
        logger.debug(f"Checking env var {env_key}: {'found' if api_key else 'not found'}")
        if api_key:
            return api_key
    # Fall back to config file
    config_key = provider_config.get('api_key')
    logger.debug(f"Checking config file: {'found' if config_key else 'not found'}")
    return config_key 