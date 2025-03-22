from argparse import BooleanOptionalAction
from enum import StrEnum
from inspect import Parameter
from typing import Annotated
from unittest.mock import MagicMock, Mock, _Call, call

import pytest

from yaru.argument import Arg, CommandArgument, _EnumAction, _parse_literal_as_boolean
from yaru.exceptions import (
    InvalidAnnotationTypeError,
    InvalidArgumentTypeHintError,
    MissingArgumentTypeHintError,
    YaruError,
)


class MockEnum(StrEnum):
    FOO = "foo"
    BAR = "bar"


@pytest.mark.parametrize(
    "command_argument",
    [
        CommandArgument("name", 0, "help", "metavar"),
    ],
)
def test_command_argument_init(command_argument: CommandArgument) -> None:
    assert command_argument.name == "name"
    assert command_argument.default == 0
    assert command_argument.help == "help"
    assert command_argument.metavar == "metavar"


@pytest.mark.parametrize(
    ["default", "expected"], [(0, True), (None, True), (CommandArgument._Empty, False)]
)
def test_command_argument_is_optional(
    default: int | None | type[CommandArgument._Empty], expected: bool
) -> None:
    assert CommandArgument("name", default=default).is_optional == expected


@pytest.mark.parametrize(
    "arg_type",
    [int, str, float, bool, MockEnum],
)
def test_command_argument_arg_type(arg_type: type) -> None:
    assert CommandArgument[arg_type]("name").arg_type is arg_type


@pytest.mark.parametrize(
    ["parameter", "expected"],
    [
        (
            Parameter("name", Parameter.POSITIONAL_OR_KEYWORD, annotation=int),
            CommandArgument[int](
                "name", default=CommandArgument._Empty, help=None, metavar=None
            ),
        ),
        (
            Parameter(
                "name", Parameter.POSITIONAL_OR_KEYWORD, default=0, annotation=int
            ),
            CommandArgument[int]("name", default=0, help=None, metavar=None),
        ),
        (
            Parameter(
                "name",
                Parameter.POSITIONAL_OR_KEYWORD,
                annotation=tuple[int],
            ),
            CommandArgument[int](
                "name", default=CommandArgument._Empty, help=None, metavar=None
            ),
        ),
        (
            Parameter(
                "name",
                Parameter.POSITIONAL_OR_KEYWORD,
                annotation=Annotated[int, Arg(help="help", metavar="metavar")],
            ),
            CommandArgument[int](
                "name", default=CommandArgument._Empty, help="help", metavar="metavar"
            ),
        ),
    ],
)
def test_command_argument_from_paramater_ok(
    parameter: Parameter, expected: CommandArgument
) -> None:
    argument = CommandArgument.from_parameter(parameter)
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
        CommandArgument.from_parameter(parameter)


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
            CommandArgument._Empty,
            call(
                "name",
                type=_parse_literal_as_boolean,
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
            CommandArgument._Empty,
            call("name", type=int, help="help", metavar="metavar"),
        ),
        (
            MockEnum,
            MockEnum.FOO,
            call(
                "--name",
                type=MockEnum,
                action=_EnumAction,
                choices=["FOO", "BAR"],
                default=MockEnum.FOO,
                help="help",
                metavar="metavar",
            ),
        ),
        (
            MockEnum,
            CommandArgument._Empty,
            call(
                "name",
                type=MockEnum,
                action=_EnumAction,
                choices=["FOO", "BAR"],
                help="help",
                metavar="metavar",
            ),
        ),
    ],
)
def test_command_argument_add_to_parser(
    arg_type: bool | int,
    default: bool | type[CommandArgument._Empty] | int,
    call: _Call,
) -> None:
    mock_add_argument = Mock()

    argument = CommandArgument[arg_type](
        "name", default=default, help="help", metavar="metavar"
    )
    argument.add_to_parser(Mock(add_argument=mock_add_argument))
    mock_add_argument.assert_has_calls([call])


@pytest.mark.parametrize(
    ["literal", "expected"],
    [("1", True), ("0", False), ("True", True), ("False", False)],
)
def test_parse_literal_as_boolean(literal: str, expected: bool) -> None:
    assert _parse_literal_as_boolean(literal) == expected


def test_enum_action() -> None:
    action, namespace = _EnumAction([], "dest", type=MockEnum), MagicMock()
    action(MagicMock(), namespace, values="FOO")
    assert getattr(namespace, action.dest) == MockEnum.FOO
