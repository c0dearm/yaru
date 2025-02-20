# YARU (やる)

[![image](https://img.shields.io/pypi/v/yaru.svg)](https://pypi.python.org/pypi/yaru)
[![image](https://img.shields.io/pypi/l/yaru.svg)](https://pypi.python.org/pypi/yaru)
[![image](https://img.shields.io/pypi/pyversions/yaru.svg)](https://pypi.python.org/pypi/yaru)
[![Actions status](https://github.com/c0dearm/yaru/actions/workflows/ci.yml/badge.svg)](https://github.com/c0dearm/yaru/actions)

Write and manage your project's development scripts with modern Python syntax.

The project's name comes from the Japanese verb やる, which means "to do".

## Highlights

- 🗂️ Lightweight package with zero dependencies.
- 🐍 Supports modern Python versions (>=3.12).
- 🚀 Simply write your development scripts as Python functions.
- 🖥️ Supports macOS, Linux, and Windows.

## Installation

If using the [uv](https://github.com/astral-sh/uv) package manager:

```bash
uv add --dev yaru
```

If using `pip`:

```bash
pip install yaru
```

## Documentation

Yaru's documentation is available at [https://github.com/c0dearm/yaru](https://github.com/c0dearm/yaru).

## Features

### A single decorator to rule them all

Simply decorate your Python functions to convert them into cli commands:

```python
# :commands.py file

from typing import Annotated
from yaru import Arg, Context, command


# Add two numbers
@command
def add_numbers(c: Context, a: int, b: int) -> None:
    """Given `a` and `b`, print the sum of both numbers to stdout."""

    print(a + b)
```

The decorated functions must be discovered by `yaru`, so they need to be in a module named `commands` at
the root of your project, for example a `commands.py` file.

The `add_numbers` command is not invokable through the cli, this is the output of `yaru --help`:

```
usage: yaru [-h] {add-numbers} ...

Project's development commands

positional arguments:
  {add-numbers}
    add-numbers  Add two numbers

options:
  -h, --help     show this help message and exit
```

For specific help on the command usage, you can do: `yaru add-numbers --help`:

```
usage: yaru add-numbers [-h] a b

Given `a` and `b`, print the sum of both numbers to stdout.

positional arguments:
  a
  b

options:
  -h, --help  show this help message and exit
```

Running the command `yaru add-numbers 42 69` in your terminal will output `111`.

### Automatated command metadata

The help text for the cli command is automatically parsed from the comments immiediatelly preceding the decorated function.
Similarly, the command's description is obtained from the function's docstrings.

Moreover, you can use annotated type hints on your function's arguments in order to add help texts to the command's parameters too:

```python
# :commands.py file

from typing import Annotated
from yaru import Arg, Context, command


# Add two numbers
@command
def add_numbers(
    c: Context,
    a: Annotated[int, Arg(help="First operand")],
    b: Annotated[int, Arg(help="Second operand")],
) -> None:
    """Given `a` and `b`, print the sum of both numbers to stdout."""

    print(a + b)
```

The `add-numbers` cli help will now display as:

```
usage: yaru add-numbers [-h] a b

Given `a` and `b`, print the sum of both numbers to stdout.

positional arguments:
  a           First operand
  b           Second operand

options:
  -h, --help  show this help message and exit
```

### Optional arguments

If you define the function's arguments as optional (keyword arguments with defaults), `yaru` will treat
them as such in the cli. For example:

```python
# :commands.py file

from yaru import Context, command


@command
def say_something(c: Context, phrase: str, twice: bool = False) -> None:
    print(phrase)
    if twice:
        print(phrase)
```

Will be handled like this:

```
usage: yaru say-something [-h] [--twice | --no-twice] phrase

positional arguments:
  phrase

options:
  -h, --help           show this help message and exit
  --twice, --no-twice
```

### Context to run commands in a shell

You may have noticed an extra first `Context` argument in all the commands. This is automatically injected
by `yaru` and provides a handy method `run` to execute instructions in your shell.

Going back to the example of number addition, we could do this in `bash` instead of `python`:

```python
# :commands.py file

from yaru import Context, command


# Add two numbers
@command
def add_numbers(c: Context, a: int, b: int) -> None:
    c.run(f"echo $(({a} + {b}))")
```

The behavior when executed is exactly the same.

## Acknowledgements

Yaru exists thanks to [pyinvoke](https://github.com/pyinvoke/invoke), which was the main inspirer.

## License

Yaru is licensed under the MIT license ([LICENSE](LICENSE) or <https://opensource.org/licenses/MIT>)
