import inspect
from argparse import (
    ArgumentParser,
    RawTextHelpFormatter,
    _SubParsersAction,
)
from functools import partial, wraps
from typing import Callable, Concatenate, Self, Sequence, overload

from yaru.argument import CommandArgument
from yaru.context import Context


class Command:
    """Commands built and registered by the @command decorator."""

    __registry: set[Self] = set()

    def __init__(
        self: Self,
        name: str,
        func: partial[Context],
        arguments: Sequence[CommandArgument] | None = None,
        help: str | None = None,
        aliases: Sequence[str] | None = None,
        prog: str | None = None,
        usage: str | None = None,
        description: str | None = None,
        epilog: str | None = None,
    ) -> None:
        self.name = name
        self.func = func
        self.arguments = arguments or []
        self.help = help
        self.aliases = aliases or []
        self.prog = prog
        self.usage = usage
        self.description = description
        self.epilog = epilog

    @staticmethod
    def parse_help(func: Callable) -> str | None:
        """Extracts the command's help text from the function's preceding comment in a single line, cleaning up all the '#'."""
        if comments := inspect.getcomments(func):
            return "".join(comments.replace("#", "").splitlines()).strip()
        return None

    @staticmethod
    def parse_description(func: Callable) -> str | None:
        """Extracts the command's description from the function's docstring."""
        if docstring := inspect.getdoc(func):
            return inspect.cleandoc(docstring)
        return None

    @staticmethod
    def parse_parameters(func: Callable) -> Sequence[CommandArgument]:
        """Parses the command's arguments from the function's signature."""
        signature = inspect.signature(func)
        return [
            CommandArgument.from_parameter(p) for p in signature.parameters.values()
        ]

    @classmethod
    def from_callable(
        cls: type[Self],
        func: Callable,
        name: str | None = None,
        aliases: Sequence[str] | None = None,
    ) -> Self:
        """Create a new `Command` instance from the given function, injecting the `Context` as the first argument."""
        func_with_context = partial(func, Context())

        return cls(
            name or func.__name__.replace("_", "-"),
            func_with_context,
            arguments=cls.parse_parameters(func_with_context),
            help=cls.parse_help(func),
            aliases=aliases,
            description=cls.parse_description(func),
        )

    @classmethod
    def registry(cls: type[Self]) -> set[Self]:
        """Access the commands registered so far."""
        return cls.__registry

    def register(self: Self) -> None:
        """Add the command to the registry."""
        self.__registry.add(self)

    def set_as_cli(self: Self, subparsers: "_SubParsersAction[ArgumentParser]") -> None:
        """Given an argparse subparser, set the command as a cli option."""
        parser = subparsers.add_parser(
            self.name,
            help=self.help,
            aliases=self.aliases,
            prog=self.prog,
            usage=self.usage,
            description=self.description,
            epilog=self.epilog,
            formatter_class=RawTextHelpFormatter,
        )
        parser.set_defaults(func=self.func)
        for argument in self.arguments:
            argument.add_to_parser(parser)


@overload
def command[**P, R](
    func: Callable[Concatenate[Context, P], R],
) -> Callable[Concatenate[Context, P], R]: ...


@overload
def command[**P, R](
    *, name: str | None = None, aliases: Sequence[str] | None = None
) -> Callable[
    [Callable[Concatenate[Context, P], R]], Callable[Concatenate[Context, P], R]
]: ...


def command[**P, R](
    func: Callable[Concatenate[Context, P], R] | None = None,
    *,
    name: str | None = None,
    aliases: Sequence[str] | None = None,
) -> (
    Callable[Concatenate[Context, P], R]
    | Callable[
        [Callable[Concatenate[Context, P], R]], Callable[Concatenate[Context, P], R]
    ]
):
    """
    Registers the given function as a `yaru` command, so that it is callable via the cli.

    Example:

    ```pydoc
    >>> from yaru import command, Context

    >>> @command
    ... def run_tests(c: Context, coverage: bool = False) -> None:
    ...     c.run("pytest", "--coverage" if coverage else "")

    ```

    This function can now be called from the cli as a command, like:
    ```sh
    yaru run-tests --coverage
    ```
    """

    def decorator(
        f: Callable[Concatenate[Context, P], R],
    ) -> Callable[Concatenate[Context, P], R]:
        Command.from_callable(f, name=name, aliases=aliases).register()

        @wraps(f)
        def wrapper(f: Callable[Concatenate[Context, P], R], *args, **kwargs) -> R:
            return f(*args, **kwargs)

        return partial(wrapper, f)

    return decorator if func is None else decorator(func)
