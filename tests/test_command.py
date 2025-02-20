from argparse import BooleanOptionalAction, RawTextHelpFormatter
from functools import partial
from inspect import Parameter
from typing import Annotated, Callable
from unittest.mock import Mock, _Call, call, patch

import pytest

from yaru.command import Arg, Command, _CommandArgument, command
from yaru.context import Context
from yaru.exceptions import (
    InvalidAnnotationTypeError,
    InvalidArgumentTypeHintError,
    MissingArgumentTypeHintError,
    YaruError,
)


@pytest.mark.parametrize(
    "command_argument",
    [
        _CommandArgument("name", int, "help", "metavar"),
    ],
)
def test_command_argument_init(command_argument: _CommandArgument) -> None:
    assert command_argument.name == "name"
    assert command_argument.default is int
    assert command_argument.help == "help"
    assert command_argument.metavar == "metavar"


@pytest.mark.parametrize(
    ["default", "expected"], [(0, True), (None, True), (_CommandArgument._Empty, False)]
)
def test_command_argument_is_optional(default: Callable, expected: bool) -> None:
    assert _CommandArgument("name", default=default).is_optional == expected


@pytest.mark.parametrize("arg_type", [int, str, float, bool])
def test_command_argument_arg_type(arg_type: type) -> None:
    assert _CommandArgument[arg_type]("name").arg_type is arg_type


@pytest.mark.parametrize(
    ["literal", "expected"],
    [("1", True), ("0", False), ("True", True), ("False", False)],
)
def test_command_argument_parse_literal_as_boolean(
    literal: str, expected: bool
) -> None:
    assert _CommandArgument.parse_literal_as_boolean(literal) == expected


@pytest.mark.parametrize(
    ["parameter", "expected"],
    [
        # Parameter("name", Parameter.POSITIONAL_OR_KEYWORD),
        (
            Parameter("name", Parameter.POSITIONAL_OR_KEYWORD, annotation=int),
            _CommandArgument[int](  # type: ignore
                "name", default=_CommandArgument._Empty, help=None, metavar=None
            ),
        ),
        (
            Parameter(
                "name", Parameter.POSITIONAL_OR_KEYWORD, default=0, annotation=int
            ),
            _CommandArgument[int]("name", default=0, help=None, metavar=None),  # type: ignore
        ),
        (
            Parameter(
                "name",
                Parameter.POSITIONAL_OR_KEYWORD,
                annotation=tuple[int],
            ),
            _CommandArgument[int](  # type: ignore
                "name", default=_CommandArgument._Empty, help=None, metavar=None
            ),
        ),
        (
            Parameter(
                "name",
                Parameter.POSITIONAL_OR_KEYWORD,
                annotation=Annotated[int, Arg(help="help", metavar="metavar")],
            ),
            _CommandArgument[int](  # type: ignore
                "name", default=_CommandArgument._Empty, help="help", metavar="metavar"
            ),
        ),
    ],
)
def test_command_argument_from_paramater_ok(
    parameter: Parameter, expected: _CommandArgument
) -> None:
    argument = _CommandArgument.from_parameter(parameter)
    assert argument.name == expected.name
    assert argument.arg_type == expected.arg_type
    assert argument.default == expected.default
    assert argument.help == expected.help
    assert argument.metavar == expected.metavar


@pytest.mark.parametrize(
    ["parameter", "exception"],
    [
        (
            Parameter("name", Parameter.POSITIONAL_OR_KEYWORD),
            MissingArgumentTypeHintError,
        ),
        (
            Parameter(
                "name", Parameter.POSITIONAL_OR_KEYWORD, annotation=Annotated[int, str]
            ),
            InvalidAnnotationTypeError,
        ),
        (
            Parameter(
                "name",
                Parameter.POSITIONAL_OR_KEYWORD,
                annotation=Annotated[int, str, str],
            ),
            InvalidArgumentTypeHintError,
        ),
    ],
)
def test_command_argument_from_paramater_invalid(
    parameter: Parameter, exception: type[YaruError]
) -> None:
    with pytest.raises(exception):
        _CommandArgument.from_parameter(parameter)


@pytest.mark.parametrize(
    ["arg_type", "default", "call"],
    [
        (
            bool,
            False,
            call(
                "--name",
                action=BooleanOptionalAction,
                default=False,
                help="help",
                metavar="metavar",
            ),
        ),
        (
            bool,
            _CommandArgument._Empty,
            call(
                "name",
                type=_CommandArgument.parse_literal_as_boolean,
                help="help",
                metavar="metavar",
            ),
        ),
        (
            int,
            0,
            call("--name", type=int, default=0, help="help", metavar="metavar"),
        ),
        (
            int,
            _CommandArgument._Empty,
            call("name", type=int, help="help", metavar="metavar"),
        ),
    ],
)
def test_command_argument_add_to_parser(
    arg_type: Callable, default: Callable, call: _Call
) -> None:
    mock_add_argument = Mock()

    argument = _CommandArgument[arg_type](
        "name", default=default, help="help", metavar="metavar"
    )
    argument.add_to_parser(Mock(add_argument=mock_add_argument))
    mock_add_argument.assert_has_calls([call])


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

    with patch("yaru.command._CommandArgument.from_parameter") as mock_from_parameter:
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
