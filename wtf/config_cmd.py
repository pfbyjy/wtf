import click
from .config import Config

@click.group(name='wtf-config')
def cli():
    """Manage WTF configuration"""
    pass

@cli.command()
@click.argument('provider')
@click.argument('api_key')
def set_key(provider: str, api_key: str):
    """Set API key for a provider"""
    config = Config()
    if provider not in config.config['providers']:
        raise click.ClickException(f"Unknown provider: {provider}")
    
    config.config['providers'][provider]['api_key'] = api_key
    config._save_config(config.config)
    click.echo(f"API key set for {provider}")

@cli.command()
@click.argument('provider')
def set_default(provider: str):
    """Set default provider"""
    config = Config()
    if provider not in config.config['providers']:
        raise click.ClickException(f"Unknown provider: {provider}")
    
    config.config['default_provider'] = provider
    config._save_config(config.config)
    click.echo(f"Default provider set to {provider}") 