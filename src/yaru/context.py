import subprocess
from typing import Self


class Context:
    def run(
        self: Self,
        *args: str,
        env: dict[str, str] | None = None,
        fallible: bool = False,
    ) -> None:
        """
        Executes the provided instructions in a shell.

        Unless `fallible` is set to `True`, the program will finish immediatelly with the
        same exit code as the failed shell command.
        """
        try:
            subprocess.run(" ".join(args), env=env, check=not fallible, shell=True)
        except subprocess.CalledProcessError as e:
            exit(e.returncode)
