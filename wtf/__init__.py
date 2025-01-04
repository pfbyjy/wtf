from .cli import cli
from .setup import initialize

def main():
    initialize()
    cli()

if __name__ == "__main__":
    main() 