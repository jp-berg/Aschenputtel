import tomllib
import unittest
from functools import cache
from pathlib import Path

from aschenputtel import gather


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
        txt_validation = {
            filename.replace(suffix, "")
            for filename in values["all"]
            if filename.endswith(suffix)
        }
        txt_test = {str(filename) for filename in gather(test_dir, suffix).keys()}

        if not_in_validation := txt_test - txt_validation:
            self.fail(
                f"{test_name}: The following {suffix}-files were discovered by aschenputtel.gather() but are not listed in the validation file: {[f + suffix for f in not_in_validation]}"
            )
        if not_in_test := txt_validation - txt_test:
            self.fail(
                f"{test_name}: The following {suffix}-files were not discovered by aschenputtel.gather() but are listed in the validation file: {[f + suffix for f in not_in_test]}"
            )

        # for test_dir in tests:
        #     test_dir_items = [f for f in test_dir.iterdir()]
        #     self.assertEqual(len(test_dir_items), 2)
        #
        #     if test_dir_items[0].is_dir():
        #         setup_dir = test_dir_items[0]
        #
        #         to_delete_file = test_dir_items[1]
        #         self.assertTrue(to_delete_file.is_file())
        #
        #     elif test_dir_items[0].is_file():
        #         to_delete_file = test_dir_items[0]
        #
        #         setup_dir = test_dir_items[1]
        #         self.assertTrue(setup_dir.is_dir())
        #     else:
        #         self.fail("Not possible")
        #
        #
        #     self.assertEqual(setup_dir.name, "dir")
        #
        #
        #     self.assertEqual(to_delete_file.name,"toDelete.txt")
        #     to_delete = [item for item in to_delete_file.read_text().split(os.linesep) if item.strip()]
