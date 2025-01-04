from pathlib import Path
import logging
from rich.logging import RichHandler
from .config import Config

def ensure_directories():
    """Ensure all required directories exist"""
    wtf_dir = Path.home() / '.config' / 'wtf'
    log_dir = wtf_dir / 'logs'
    
    # Create directories
    wtf_dir.mkdir(parents=True, exist_ok=True)
    log_dir.mkdir(parents=True, exist_ok=True)
    
    return wtf_dir, log_dir

def setup_logging(log_dir: Path):
    """Configure logging"""
    log_file = log_dir / 'wtf.log'
    
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            RichHandler(level=logging.ERROR, show_time=False, show_path=False)
        ]
    )
    
    return log_file

def initialize():
    """Initialize WTF environment"""
    # Create directories
    wtf_dir, log_dir = ensure_directories()
    
    # Setup logging
    log_file = setup_logging(log_dir)
    
    # Initialize config (this will create default config if it doesn't exist)
    config = Config()
    
    # Show first run message if needed
    config.check_first_run()
    
    return config 

def get_log_file():
    """Get path to log file"""
    return Path.home() / '.config' / 'wtf' / 'logs' / 'wtf.log' 