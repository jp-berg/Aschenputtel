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
import unittest
from abc import ABC, abstractmethod
from functools import cache, cached_property
from pathlib import Path
from typing import Any

import tomli  # Not tomllib so Python 3.10 can still be used

from aschenputtel import gather, get_to_copy, get_to_delete


@cache
def get_tests_dir() -> Path:
    parent_dir = Path(__file__).parent
    return parent_dir / "testdirectory"


class AschenputtelTest(ABC, unittest.TestCase):

    @abstractmethod
    def get_dir_name(self) -> str: ...

    @cached_property
    def test_dir(self) -> Path:
        return get_tests_dir() / self.get_dir_name()

    @cached_property
    def validation_info(self) -> dict[str, Any]:
        validation_file = self.test_dir / "validation.toml"
        with validation_file.open("rb") as vf:
            d = tomli.load(vf)
            return d

    @cached_property
    def test_dirs(self) -> dict[str, Path]:
        return {f.name: f for f in self.test_dir.iterdir() if f.is_dir()}

    def test_testdata(self) -> None:

        if not_in_toml := self.test_dirs.keys() - self.validation_info.keys():
            self.fail(
                f"The following directories are not described in validation.toml: {[self.test_dirs[name] for name in not_in_toml]}"
            )
        if not_a_dir := self.validation_info.keys() - self.test_dirs.keys():
            self.fail(
                f"The following validation.toml-entries have no directory in  {self.test_dir}: {not_a_dir}"
            )

    def _test_gather_for(
        self, test_name: str, values: list[str], test_dir: Path, suffix: str
    ) -> None:
        validation_files = {
            filename.replace(suffix, "")
            for filename in values
            if filename.endswith(suffix)
        }
        found_files = {str(filename) for filename in gather(test_dir, suffix).keys()}

        if not_in_validation := found_files - validation_files:
            self.fail(
                f"{test_name}: The following {suffix}-files were discovered by aschenputtel.gather() but are not listed in the validation file: {[f + suffix for f in not_in_validation]}"
            )
        if not_in_test := validation_files - found_files:
            self.fail(
                f"{test_name}: The following {suffix}-files were not discovered by aschenputtel.gather() but are listed in the validation file: {[f + suffix for f in not_in_test]}"
            )

    def _validate_identified_files(
        self, test_name: str, identified: list[Path], validation: list[Path]
    ) -> None:
        identified_set = set(identified)
        self.assertEqual(len(identified), len(identified_set))

        validation_set = set(validation)
        self.assertEqual(len(validation), len(validation_set))

        if not_in_validation := identified_set - validation_set:
            self.fail(
                f"{test_name}: The following files are not in the validation-set: {not_in_validation}"
            )
        if not_identified := validation_set - identified_set:
            self.fail(
                f"{test_name}: The following files are not identified: {not_identified}"
            )


class TestInSameDir(AschenputtelTest):

    def get_dir_name(self) -> str:
        return "inSameDir"

    def test_gather(self) -> None:

        test_dir: Path
        for test_name, values in self.validation_info.items():
            with self.subTest(name=test_name):
                test_dir = self.test_dirs[test_name]
                self._test_gather_for(test_name, values["all"], test_dir, ".txt")
                self._test_gather_for(test_name, values["all"], test_dir, ".md")

    def test_get_to_delete(self) -> None:

        for test_name, values in self.validation_info.items():
            with self.subTest(name=test_name):
                test_dir = self.test_dirs[test_name]

                to_delete_list = get_to_delete(test_dir, ".txt", test_dir, ".md")
                validation_list = [test_dir / value for value in values["to_delete"]]

                self._validate_identified_files(
                    test_name, to_delete_list, validation_list
                )


class TestInDifferentDir(AschenputtelTest):

    def get_dir_name(self) -> str:
        return "inDifferentDir"

    @cached_property
    def in_same_dir(self) -> TestInSameDir:
        return TestInSameDir()

    def test_testdata(self) -> None:
        super().test_testdata()

        if not_a_dir := self.validation_info.keys() - self.in_same_dir.test_dirs.keys():
            self.fail(
                f"The following validation.toml-entries have no directory in {self.in_same_dir.test_dir}: {not_a_dir}"
            )

    def test_gather_md2txt(self) -> None:
        source_dir: Path
        target_dir: Path
        for test_name, values in self.validation_info.items():
            with self.subTest(name=test_name):
                source_dir = self.in_same_dir.test_dirs[test_name]
                self._test_gather_for(
                    test_name, values["md2txt"]["all_origin"], source_dir, ".md"
                )
                target_dir = self.test_dirs[test_name]
                self._test_gather_for(
                    test_name, values["md2txt"]["all_destination"], target_dir, ".txt"
                )

    def test_gather_txt2md(self) -> None:
        source_dir: Path
        target_dir: Path
        for test_name, values in self.validation_info.items():
            with self.subTest(name=test_name):
                source_dir = self.in_same_dir.test_dirs[test_name]
                self._test_gather_for(
                    test_name, values["txt2md"]["all_origin"], source_dir, ".txt"
                )
                target_dir = self.test_dirs[test_name]
                self._test_gather_for(
                    test_name, values["txt2md"]["all_destination"], target_dir, ".md"
                )

    def test_get_to_delete_md2txt(self) -> None:
        source_dir: Path
        target_dir: Path
        for test_name, values in self.validation_info.items():
            with self.subTest(name=test_name):
                source_dir = self.in_same_dir.test_dirs[test_name]
                target_dir = self.test_dirs[test_name]
                to_delete_list = get_to_delete(source_dir, ".md", target_dir, ".txt")
                validation_list = [
                    target_dir / value for value in values["md2txt"]["to_delete"]
                ]

                self._validate_identified_files(
                    test_name, to_delete_list, validation_list
                )

    def test_get_to_delete_txt2md(self) -> None:
        source_dir: Path
        target_dir: Path
        for test_name, values in self.validation_info.items():
            with self.subTest(name=test_name):
                source_dir = self.in_same_dir.test_dirs[test_name]
                target_dir = self.test_dirs[test_name]
                to_delete_list = get_to_delete(source_dir, ".txt", target_dir, ".md")
                validation_list = [
                    target_dir / value for value in values["txt2md"]["to_delete"]
                ]

                self._validate_identified_files(
                    test_name, to_delete_list, validation_list
                )

    def test_get_to_copy_md2txt(self) -> None:
        source_dir: Path
        target_dir: Path
        for test_name, values in self.validation_info.items():
            with self.subTest(name=test_name):
                source_dir = self.in_same_dir.test_dirs[test_name]
                target_dir = self.test_dirs[test_name]
                to_copy_list = [
                    to_copy[1]
                    for to_copy in get_to_copy(source_dir, ".md", target_dir, ".txt")
                ]
                validation_list = [
                    target_dir / value for value in values["md2txt"]["to_copy"]
                ]
                self._validate_identified_files(
                    test_name, to_copy_list, validation_list
                )

    def test_get_to_copy_txt2md(self) -> None:
        source_dir: Path
        target_dir: Path
        for test_name, values in self.validation_info.items():
            with self.subTest(name=test_name):
                source_dir = self.in_same_dir.test_dirs[test_name]
                target_dir = self.test_dirs[test_name]
                to_copy_list = [
                    to_copy[1]
                    for to_copy in get_to_copy(source_dir, ".txt", target_dir, ".md")
                ]
                validation_list = [
                    target_dir / value for value in values["txt2md"]["to_copy"]
                ]
                self._validate_identified_files(
                    test_name, to_copy_list, validation_list
                )


del AschenputtelTest
