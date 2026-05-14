"""Entry point: python3 -m cli_anything.viraltrends"""
import sys
from cli_anything.viraltrends.viraltrends_cli import main, _launch_repl

if __name__ == "__main__":
    if len(sys.argv) == 1:
        _launch_repl()
    else:
        main()
