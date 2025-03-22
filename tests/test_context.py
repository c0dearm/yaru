from subprocess import CalledProcessError
from unittest.mock import patch

from yaru.context import Context


def test_context_run() -> None:
    context = Context()
    with patch("yaru.context.subprocess.run") as mock_run:
        context.run("a", "b", "c", env={"TEST": "1"}, fallible=True)
        mock_run.assert_called_once_with(
            "a b c", env={"TEST": "1"}, check=False, shell=True
        )


@patch("yaru.context.subprocess.run")
@patch("yaru.context.exit")
def test_context_run_fallible(mock_exit, mock_run) -> None:
    context = Context()
    with (
        patch(
            "yaru.context.subprocess.run", side_effect=CalledProcessError(1, "")
        ) as mock_run,
        patch("yaru.context.exit") as mock_exit,
    ):
        context.run("a", "b", "c", env={"TEST": "1"}, fallible=False)
        mock_run.assert_called_once_with(
            "a b c", env={"TEST": "1"}, check=True, shell=True
        )
        mock_exit.assert_called_once_with(1)
