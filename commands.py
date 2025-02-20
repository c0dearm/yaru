from typing import Annotated

from yaru import Arg, Context, command


# Run the `yaru` test suite
@command
def run_tests(
    c: Context,
    docs: Annotated[bool, Arg(help="Include doctest examples")] = False,
    coverage: Annotated[bool, Arg(help="Run with coverage report")] = False,
) -> None:
    """
    Execute all the project's unit tests with optional coverage.
    """
    c.run(
        "pytest", "--doctest-modules" if docs else "", "--cov=yaru" if coverage else ""
    )
