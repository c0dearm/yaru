import argparse
import os
import sys
from importlib import import_module

from yaru.command import Arg, Command, command
from yaru.context import Context


def main() -> None:
    """Main entrypoint for `yaru`. Collects the registered commands in the `commands` module and builds the cli."""
    sys.path.append(os.path.join(os.getcwd()))
    import_module("commands")

    parser = argparse.ArgumentParser(description="Project's development commands")
    subparsers = parser.add_subparsers(dest="command", required=True)

    for c in Command.registry():
        c.set_as_cli(subparsers)

    args = parser.parse_args()
    kwargs = {k: v for k, v in vars(args).items() if k not in ("command", "func")}
    args.func(**kwargs)


__all__ = ["command", "Context", "Arg"]
