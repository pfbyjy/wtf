from pathlib import Path
import json
from datetime import datetime
from typing import List, Dict, Optional
from rich.console import Console
from rich.table import Table
from rich import box

class History:
    def __init__(self):
        self.history_file = Path.home() / '.config' / 'wtf' / 'history.json'
        self.history_file.parent.mkdir(parents=True, exist_ok=True)
        self.console = Console()
        
    def add(self, prompt: str, command: str, success: bool = True, metadata: Optional[Dict] = None):
        """Add a command to history with metadata"""
        history = self.load()
        history.append({
            "timestamp": datetime.now().isoformat(),
            "prompt": prompt,
            "command": command,
            "success": success,
            "metadata": metadata or {}
        })
        self.save(history[-1000:])  # Keep last 1000 commands
        
    def load(self) -> List[Dict]:
        if self.history_file.exists():
            return json.loads(self.history_file.read_text())
        return []
        
    def save(self, history: List[Dict]):
        self.history_file.write_text(json.dumps(history, indent=2))

    def show(self, limit: int = 10):
        """Display history in a rich table"""
        history = self.load()
        
        table = Table(
            box=box.ROUNDED,
            title="Command History",
            show_lines=True
        )
        
        table.add_column("When", style="cyan", width=12)
        table.add_column("Prompt", style="green")
        table.add_column("Command", style="yellow")
        table.add_column("Provider", style="blue", width=10)
        table.add_column("Model", style="magenta", width=15)
        table.add_column("Latency", style="cyan", width=8)
        table.add_column("Status", justify="center", width=8)
        
        # Get the last 'limit' entries and reverse them
        entries = list(reversed(history[-limit:]))
        
        for entry in entries:
            # Format timestamp
            dt = datetime.fromisoformat(entry['timestamp'])
            when = self._format_time(dt)
            
            # Get metadata
            metadata = entry.get('metadata', {})
            provider = metadata.get('provider', '-')
            model = metadata.get('model', '-')
            latency = f"{metadata.get('latency', 0):.2f}s"
            
            # Format status with color
            success = entry.get('success', True)
            status = f"[{'green' if success else 'red'}]{'✓' if success else '✗'}[/]"
            
            table.add_row(
                when,
                entry['prompt'],
                entry['command'],
                provider,
                model,
                latency,
                status
            )
        
        self.console.print(table)

    def _format_time(self, dt: datetime) -> str:
        """Format timestamp in a human-readable way"""
        now = datetime.now()
        delta = now - dt
        
        if delta.days == 0:
            if delta.seconds < 60:
                return "just now"
            if delta.seconds < 3600:
                return f"{delta.seconds // 60}m ago"
            return f"{delta.seconds // 3600}h ago"
        if delta.days == 1:
            return "yesterday"
        if delta.days < 7:
            return f"{delta.days}d ago"
        return dt.strftime("%Y-%m-%d") 