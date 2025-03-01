import tomllib
import unittest
from functools import cache
from pathlib import Path

from aschenputtel import gather, get_to_delete


@cache
def get_tests_dir() -> Path:
    parent_dir = Path(__file__).parent
    return parent_dir / "testdirectory"


@cache
def get_in_same_dir() -> Path:
    return get_tests_dir() / "inSameDir"


@cache
def get_validation_info() -> dict[str, dict[str, list[str]]]:
    validation_file = get_in_same_dir() / "validation.toml"
    with validation_file.open("rb") as vf:
        d = tomllib.load(vf)
        return d


@cache
def get_test_dirs() -> dict[str, Path]:
    return {f.name: f for f in get_in_same_dir().iterdir() if f.is_dir()}


class TestInSameDir(unittest.TestCase):

    def test_testdata(self) -> None:
        test_dirs = get_test_dirs()
        tests = get_validation_info()

        if not_in_toml := test_dirs.keys() - tests.keys():
            self.fail(
                f"The following directories are not described in validation.toml: {[test_dirs[name] for name in not_in_toml]}"
            )
        if not_a_dir := tests.keys() - test_dirs.keys():
            self.fail(
                f"The following validation.toml-entries have no directory: {not_a_dir}"
            )

    def test_gather(self) -> None:
        test_dirs = get_test_dirs()
        tests = get_validation_info()

        test_dir: Path
        for test_name, values in tests.items():
            test_dir = test_dirs[test_name]
            self._test_gather_for(test_name, values, test_dir, ".txt")
            self._test_gather_for(test_name, values, test_dir, ".md")

    def _test_gather_for(
        self, test_name: str, values: dict[str, list[str]], test_dir: Path, suffix: str
    ) -> None:
        validation_files = {
            filename.replace(suffix, "")
            for filename in values["all"]
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

    def test_get_to_delete(self) -> None:
        test_dirs = get_test_dirs()
        tests = get_validation_info()

        for test_name, values in tests.items():
            test_dir = test_dirs[test_name]
            to_delete_list = get_to_delete(test_dir, ".txt", test_dir, ".md")

            to_delete_set = set(to_delete_list)
            self.assertEqual(len(to_delete_list), len(to_delete_set))

            validation_list = [test_dir / value for value in values["to_delete"]]
            validation_set = set(validation_list)
            self.assertEqual(len(validation_list), len(validation_set))

            if not_in_validation := to_delete_set - validation_set:
                self.fail(
                    f"{test_name}: The following files were erroneously marked for deletion: {not_in_validation}"
                )
            if not_in_to_delete := validation_set - to_delete_set:
                self.fail(
                    f"{test_name}: The following files should be deleted but were not marked as such: {not_in_to_delete}"
                )
