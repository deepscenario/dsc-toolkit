"""Unified CLI entry point for DeepScenario Toolkit."""

from __future__ import annotations

import argparse

from dsc_toolkit.plot_annotations_3d import main as plot_annotations_3d_main
from dsc_toolkit.plot_annotations_georeferenced import main as plot_annotations_georeferenced_main
from dsc_toolkit.render_orthophoto import main as render_orthophoto_main

COMMANDS = {
    'plot_annotations_3d': plot_annotations_3d_main,
    'plot_annotations_georeferenced': plot_annotations_georeferenced_main,
    'render_orthophoto': render_orthophoto_main,
}


def parse_args(argv: list[str] | None = None) -> tuple[str, list[str]]:
    parser = argparse.ArgumentParser(description='Toolkit for visualizing and working with DeepScenario datasets',
                                     add_help=False)
    parser.add_argument('command', choices=list(COMMANDS.keys()), help='Name of the command to run')

    args, remaining_argv = parser.parse_known_args(argv)
    return args.command, remaining_argv


def main(argv: list[str] | None = None) -> None:
    """Main dsc-toolkit CLI entry point."""
    command, command_argv = parse_args(argv)
    COMMANDS[command](command_argv)


if __name__ == '__main__':
    main()
