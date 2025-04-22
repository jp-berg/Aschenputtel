# Copyright (C) 2025 Jan Philipp Berg <git.7ksst@aleeas.com>
#
# This file is part of aschenputtel.
#
# aschenputtel is free software: you can redistribute it and/or modify it under the
# terms of the GNU General Public License as published by the Free Software Foundation,
# either version 3 of the License, or (at your option) any later version.
#
# aschenputtel is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A
# PARTICULAR PURPOSE.
# See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along with
# aschenputtel. If not, see <https://www.gnu.org/licenses/>.
from typing import Final

import nox

nox.options.default_venv_backend = "uv"

PYTHON_VERSION_LIST: Final[list[str]] = ["3.9", "3.10", "3.11", "3.12", "3.13"]


@nox.session
def dev(session: nox.Session) -> None:
    """Creates the developement environment"""
    session.run("uv", "sync")


@nox.session
def tidy(session: nox.Session) -> None:
    """Cleans the code"""
    session.install("isort")
    session.run("isort", ".")

    session.install("black")
    session.run("black", ".")

    session.install("autoflake")
    session.run("autoflake", ".-r")
    session.notify("check")


@nox.session(python=PYTHON_VERSION_LIST)
def check(session: nox.Session) -> None:
    """Runs static analysis and tests"""
    session.install("mypy")
    session.run("mypy")

    session.install("tomli")  # stupid hack to make the tests pass
    session.run("python3", "-m", "unittest", "test/aschenputtel_test.py")
