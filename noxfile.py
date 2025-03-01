from typing import Final

import nox

nox.options.default_venv_backend = "uv"

PYTHON_VERSION_LIST: Final[list[str]] = ["3.9", "3.10", "3.11", "3.12", "3.13"]


@nox.session
def tidy(session: nox.Session) -> None:
    """Cleans the code"""
    session.install("isort")
    session.run("isort", ".")

    session.install("black")
    session.run("black", ".")

    session.install("autoflake")
    session.run("autoflake", "." "-r")
    session.notify("check")


@nox.session(python=PYTHON_VERSION_LIST)
def check(session: nox.Session) -> None:
    """Runs static analysis and tests"""
    session.install("mypy")
    session.run("mypy")

    session.install("tomli")  # stupid hack to make the tests pass
    session.run("python3", "-m", "unittest", "test/aschenputtel_test.py")
