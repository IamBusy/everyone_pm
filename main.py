from __future__ import annotations

import sys

from specforge.main import app


def main() -> None:
    # UX requirement: `python main.py "I want to build a todo app"`
    # If the first arg isn't a known subcommand/flag, treat it as the initial prompt.
    argv = sys.argv[1:]

    # Pass through help/version flags.
    if any(a in {"-h", "--help"} for a in argv):
        app(prog_name="specforge", args=argv)
        return

    if argv and argv[0] != "new":
        # Treat everything after main.py as the initial prompt.
        prompt = " ".join(argv)
        argv = [prompt]

    app(prog_name="specforge", args=argv)


if __name__ == "__main__":
    main()
