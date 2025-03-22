import ast
import inspect
from argparse import Action, ArgumentParser, BooleanOptionalAction, Namespace
from dataclasses import dataclass
from enum import Enum
from typing import Any, Self, Sequence, get_args

from yaru.exceptions import (
    InvalidAnnotationTypeError,
    InvalidArgumentTypeHintError,
    MissingArgumentTypeHintError,
)


@dataclass
class Arg:
    """Used to provide extra metadata for an argument as part of an annotated type."""

    help: str | None = None
    metavar: str | tuple[str, ...] | None = None


class CommandArgument[T: int | float | str | bool | Enum]:
    """Used by the Command class to store the information concerning its cli arguments."""

    class _Empty:
        """Used to represent an argument without default value."""

    def __init__(
        self: Self,
        name: str,
        default: T | None | type[_Empty] = _Empty,
        help: str | None = None,
        metavar: str | tuple[str, ...] | None = None,
    ) -> None:
        self.name = name
        self.default = default
        self.help = help
        self.metavar = metavar

    @property
    def is_optional(self) -> bool:
        """`true` if the argument is optional, `false` otherwise."""
        return self.default != self._Empty

    @property
    def arg_type(self) -> type[T]:
        """The type of this argument."""
        return get_args(self.__orig_class__)[0]  # type: ignore

    @classmethod
    def from_parameter(
        cls: type[Self], parameter: inspect.Parameter
    ) -> "CommandArgument":
        """Builds an instance of this class given a function parameter obtained by `inspect.signature`."""
        if parameter.annotation == parameter.empty:
            raise MissingArgumentTypeHintError(
                f"'{parameter.name}' argument is not annotated, type hints are mandatory."
            )

        match get_args(parameter.annotation):
            case ():
                arg_type = parameter.annotation
                metadata = Arg()
            case (arg_type,):
                metadata = Arg()
            case (arg_type, metadata):
                if not isinstance(metadata, Arg):
                    raise InvalidAnnotationTypeError(
                        f"'{parameter.name}' argument annotation must be of type {Arg}, found: {parameter.annotation}."
                    )
            case _:
                raise InvalidArgumentTypeHintError(
                    f"'{parameter.name}' argument couldn't be interpreted as a valid command argument, found: {parameter.annotation} ."
                )

        return CommandArgument[arg_type](
            parameter.name,
            default=cls._Empty
            if parameter.default == parameter.empty
            else parameter.default,
            help=metadata.help,
            metavar=metadata.metavar,
        )

    def add_to_parser(self: Self, parser: ArgumentParser) -> None:
        """Given a command parser, adds itself as an argument of that command."""
        if self.arg_type is bool:
            if self.is_optional:
                parser.add_argument(
                    f"--{self.name}",
                    action=BooleanOptionalAction,
                    default=self.default,
                    help=self.help,
                    metavar=self.metavar,
                )
            else:
                parser.add_argument(
                    self.name,
                    type=_parse_literal_as_boolean,
                    help=self.help,
                    metavar=self.metavar,
                )
        elif issubclass(self.arg_type, Enum):
            if self.is_optional:
                parser.add_argument(
                    f"--{self.name}",
                    type=self.arg_type,
                    action=_EnumAction,
                    choices=[item.name for item in self.arg_type],
                    default=self.default,
                    help=self.help,
                    metavar=self.metavar,
                )
            else:
                parser.add_argument(
                    self.name,
                    type=self.arg_type,
                    action=_EnumAction,
                    choices=[item.name for item in self.arg_type],
                    help=self.help,
                    metavar=self.metavar,
                )
        else:
            if self.is_optional:
                parser.add_argument(
                    f"--{self.name}",
                    type=self.arg_type,
                    default=self.default,
                    help=self.help,
                    metavar=self.metavar,
                )
            else:
                parser.add_argument(
                    self.name, type=self.arg_type, help=self.help, metavar=self.metavar
                )


class _EnumAction(Action):
    """
    Argparse action for handling Enums.
    """

    def __init__(self, *args, **kwargs) -> None:
        self._enum_type: type[Enum] = kwargs.pop("type")
        super().__init__(*args, **kwargs)

    def __call__(
        self,
        parser: ArgumentParser,
        namespace: Namespace,
        values: str | Sequence[Any] | None,
        option_string: str | None = None,
    ) -> None:
        # Convert value back into an Enum
        value = self._enum_type[values]  # type: ignore
        setattr(namespace, self.dest, value)


def _parse_literal_as_boolean(literal: str) -> bool:
    """
    Used by argparse when a non-optional boolean is used as a command argument.
    It interprets strings like '1', '0', 'true', 'false' as booleans.
    """
    return bool(ast.literal_eval(literal))
