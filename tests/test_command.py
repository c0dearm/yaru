from argparse import RawTextHelpFormatter
from functools import partial
from inspect import Parameter
from unittest.mock import Mock, call, patch

import pytest

from yaru.command import Command, command
from yaru.context import Context


@pytest.mark.parametrize(
    "command",
    [
        Command("name", Mock, [], "help", [], "prog", "usage", "description", "epilog"),
        Command(
            "name", Mock, None, "help", None, "prog", "usage", "description", "epilog"
        ),
    ],
)
def test_command_init(command: Command) -> None:
    assert command.name == "name"
    assert command.func == Mock
    assert command.arguments == []
    assert command.help == "help"
    assert command.aliases == []
    assert command.prog == "prog"
    assert command.usage == "usage"
    assert command.description == "description"
    assert command.epilog == "epilog"


def test_command_parse_help() -> None:
    ### A mock function with a
    ### pair of lines of comments
    def function_with_comments(): ...

    def function_without_comments(): ...

    assert (
        Command.parse_help(function_with_comments)
        == "A mock function with a pair of lines of comments"
    )
    assert Command.parse_help(function_without_comments) is None


def test_command_parse_description() -> None:
    def function_with_docstring() -> None:
        """
        A mock function with a
        pair of lines of docstring
        """

    def function_without_docstring(): ...

    assert (
        Command.parse_description(function_with_docstring)
        == "A mock function with a\npair of lines of docstring"
    )
    assert Command.parse_description(function_without_docstring) is None


def test_command_parse_parameters() -> None:
    def function_with_args(a: int, b: str): ...

    with patch("yaru.command.CommandArgument.from_parameter") as mock_from_parameter:
        parameters = Command.parse_parameters(function_with_args)
        mock_from_parameter.assert_has_calls(
            [
                call(Parameter("a", Parameter.POSITIONAL_OR_KEYWORD, annotation=int)),
                call(Parameter("b", Parameter.POSITIONAL_OR_KEYWORD, annotation=str)),
            ]
        )

    assert len(parameters) == 2


@pytest.mark.parametrize(
    ["name", "expected"], [("dummy_name", "dummy_name"), (None, "dummy-function")]
)
def test_command_from_callable(name: str | None, expected: str) -> None:
    def dummy_function(): ...

    with (
        patch("yaru.command.Command.parse_parameters") as mock_parse_parameters,
        patch("yaru.command.Command.parse_help") as mock_parse_help,
        patch("yaru.command.Command.parse_description") as mock_parse_description,
    ):
        command = Command.from_callable(dummy_function, name=name)
        mock_parse_parameters.assert_called_once_with(command.func)
        mock_parse_help.assert_called_once_with(dummy_function)
        mock_parse_description.assert_called_once_with(dummy_function)

    assert command.name == expected
    assert isinstance(command.func, partial)
    assert command.func.func == dummy_function
    assert isinstance(command.func.args[0], Context)
    assert command.arguments == mock_parse_parameters.return_value
    assert command.help == mock_parse_help.return_value
    assert command.description == mock_parse_description.return_value


def test_command_register() -> None:
    command = Command("name", Mock)
    with patch("yaru.command.Command._Command__registry", set()):
        command.register()
        assert Command.registry() == {command}


def test_command_set_as_cli() -> None:
    mock_set_defaults = Mock()
    mock_add_to_parser = Mock()
    mock_parser = Mock(set_defaults=mock_set_defaults)
    mock_add_parser = Mock(return_value=mock_parser)
    mock_subparsers = Mock(add_parser=mock_add_parser)
    mock_argument = Mock(add_to_parser=mock_add_to_parser)

    command = Command("name", Mock, arguments=[mock_argument])
    command.set_as_cli(mock_subparsers)
    mock_add_parser.assert_called_once_with(
        command.name,
        help=command.help,
        aliases=command.aliases,
        prog=command.prog,
        usage=command.usage,
        description=command.description,
        epilog=command.epilog,
        formatter_class=RawTextHelpFormatter,
    )
    mock_set_defaults.assert_called_once_with(func=Mock)
    mock_add_to_parser.assert_called_once_with(mock_add_parser.return_value)


def test_command_decorator_with_args() -> None:
    mock_register = Mock()
    mock_func = Mock(return_value=0)

    with patch(
        "yaru.command.Command.from_callable", return_value=Mock(register=mock_register)
    ) as mock_from_callable:
        decorated = command(name="name", aliases=["alias"])(mock_func)
        mock_from_callable.assert_called_once_with(
            mock_func, name="name", aliases=["alias"]
        )
        mock_register.assert_called_once()

    assert decorated(Context()) == 0


def test_command_decorator_without() -> None:
    mock_register = Mock()
    mock_func = Mock(return_value=0)

    with patch(
        "yaru.command.Command.from_callable", return_value=Mock(register=mock_register)
    ) as mock_from_callable:
        decorated = command(mock_func)
        mock_from_callable.assert_called_once_with(mock_func, name=None, aliases=None)
        mock_register.assert_called_once()

    assert decorated(Context()) == 0
