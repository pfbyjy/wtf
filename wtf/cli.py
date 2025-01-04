import os
import click
import subprocess
import pyperclip
from typing import Optional
import logging
from .config import Config
from .providers import get_provider
from rich.console import Console
from rich.status import Status
from .history import History
from .setup import get_log_file
import time
from rich.table import Table
from rich import box

logger = logging.getLogger('wtf')

def translate_command(command: tuple, provider: Optional[str], model: Optional[str], execute: bool, debug: bool):
    """Convert natural language to shell commands"""
    console = Console(stderr=True)
    history = History()
    
    status = Status("[bold blue]Thinking...", console=console)
    status.start()
    
    try:
        start_time = time.time()
        config = Config()
        provider_name = provider or config.config['default_provider']
        provider_config = config.get_provider_config(provider_name)
        model = model or provider_config['default_model']

        ai_provider = get_provider(provider_name, config.config)
        shell_command = ai_provider.get_shell_command(' '.join(command), model)
        latency = time.time() - start_time

        status.stop()

        metadata = {
            "provider": provider_name,
            "model": model,
            "latency": latency
        }

        if execute:
            if not click.confirm(f"\nAbout to execute: {shell_command}\nContinue?", err=True):
                raise click.Abort()
            logger.info(f"Executing: {shell_command}")
            click.echo(f"Executing: {shell_command}", err=True)
            os.system(shell_command)
            history.add(' '.join(command), shell_command, success=True, metadata=metadata)
        else:
            logger.info(f"Generated command: {shell_command}")
            click.echo(shell_command)
            try:
                pyperclip.copy(shell_command)
                click.echo("(copied to clipboard)", err=True)
            except Exception as e:
                logger.debug(f"Failed to copy to clipboard: {e}")
            history.add(' '.join(command), shell_command, success=True, metadata=metadata)
    except Exception as e:
        status.stop()
        logger.exception("Error during command translation")
        history.add(' '.join(command), "", success=False, metadata={"error": str(e)})
        raise click.ClickException(str(e))
    finally:
        status.stop()

@click.command()
@click.argument('command', nargs=-1, required=False)
@click.option('-p', '--provider', help='AI provider to use')
@click.option('-m', '--model', help='Model to use')
@click.option('-e', '--execute', is_flag=True, help='Execute the generated command')
@click.option('-d', '--debug', is_flag=True, help='Show debug information')
@click.option('--history', is_flag=True, help='Show command history')
@click.option('--logs', is_flag=True, help='Show debug logs')
@click.option('--show-config', is_flag=True, help='Show current configuration')
@click.option('-n', '--lines', default=20, help='Number of lines to show for logs/history')
@click.option('-f', '--follow', is_flag=True, help='Follow log output')
def cli(command: tuple, provider: Optional[str], model: Optional[str], execute: bool, 
        debug: bool, history: bool, logs: bool, show_config: bool, lines: int, follow: bool):
    """WTF - Convert natural language to shell commands"""
    
    if show_config:
        config = Config()
        console = Console()
        
        table = Table(
            title="[bold]WTF Configuration[/]",
            box=box.ROUNDED,
            show_header=True,
            header_style="bold cyan",
            show_lines=True,
            padding=(0, 1)
        )
        
        table.add_column("Setting", style="cyan", no_wrap=True)
        table.add_column("Value", style="green")
        
        # Global settings section
        table.add_row(
            "[bold]Global Settings[/]",
            "",
            style="bright_black"
        )
        table.add_row(
            "  Default Provider",
            config.config['default_provider']
        )
        table.add_row(
            "  Default Model",
            config.config['default_model']
        )
        
        # Provider sections
        for provider, settings in config.config['providers'].items():
            table.add_section()
            table.add_row(
                f"[bold]{provider.title()} Provider[/]",
                "",
                style="bright_black"
            )
            
            # API Key status with color
            key_status = "[green]✓ Set[/]" if config.get_api_key(provider) else "[red]✗ Not Set[/]"
            table.add_row("  API Key", key_status)
            
            # Default model
            table.add_row(
                "  Default Model",
                f"[yellow]{settings['default_model']}[/]"
            )
            
            # Available models as bullet points
            models = "\n".join(f"• {model}" for model in settings['models'])
            table.add_row("  Available Models", models)
        
        console.print()
        console.print(table)
        console.print()
        console.print(f"Config file: [blue]{config.config_file}[/]")
        console.print()
        return
        
    if history:
        History().show(limit=lines)
        return
        
    if logs:
        log_file = get_log_file()
        console = Console()
        
        if follow:
            try:
                subprocess.run(['tail', '-f', str(log_file)])
            except KeyboardInterrupt:
                pass
        else:
            if log_file.exists():
                with open(log_file) as f:
                    last_lines = list(f)[-lines:]
                    for line in last_lines:
                        console.print(line.strip())
            else:
                console.print("No logs found", style="yellow")
        return

    if not command:
        raise click.UsageError("Please provide a command description")
        
    translate_command(command, provider, model, execute, debug) 