from unittest.mock import patch

from yaru.context import Context


def test_context_run() -> None:
    context = Context()
    with patch("yaru.context.subprocess.run") as mock_run:
        context.run("a", "b", "c", env={"TEST": "1"}, fallible=True)
        mock_run.assert_called_once_with(
            "a b c", env={"TEST": "1"}, check=False, shell=True
        )
