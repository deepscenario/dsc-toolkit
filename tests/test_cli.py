import shlex

import pytest

from dsc_toolkit.cli import main


def test_cli_invalid_command() -> None:
    with pytest.raises(SystemExit, match='2'):
        main()

    with pytest.raises(SystemExit, match='2'):
        main(shlex.split('invalid_command'))

    with pytest.raises(SystemExit, match='2'):
        main(shlex.split('--help'))


def test_cli_valid_command() -> None:
    with pytest.raises(SystemExit, match='0'):
        main(shlex.split('plot_annotations_3d --help'))
