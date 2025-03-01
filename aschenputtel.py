import argparse
import os
from argparse import ArgumentError
from pathlib import Path
from typing import NamedTuple

parser = argparse.ArgumentParser(
    prog="Aschenputtel",
    description="Moves .DNG-Files without matching .JPG files into a separate folder",
)

# TODO --delete --verbose --quiet --version --create-with --move-to --delete-empty-dirs
source_action = parser.add_argument(
    "source", nargs=1, help="The directory containing the state to replicate"
)
target_action = parser.add_argument(
    "-t",
    "--target",
    nargs=1,
    help="The directory to synchronize with 'source' (may be the same as 'source'",
)
source_suffix_action = parser.add_argument(
    "-sfs",
    "--source-file-suffix",
    nargs=1,
    help="The file-suffix of the files representing the source",
)
target_suffix_action = parser.add_argument(
    "-tfs",
    "--target-file-suffix",
    required=False,
    nargs=1,
    help="The file-suffix of the files representing the target",
)
dry_run_action = parser.add_argument(
    "-d",
    "--dry-run",
    action="store_true",
    help="Just show the files that would have been deleted without actually deleting them",
)


class AschenputtelArgs(NamedTuple):
    source: Path
    target: Path
    source_suffix: str | None = None
    target_suffix: str | None = None
    dry_run: bool = False


def extract_args() -> AschenputtelArgs:
    parsed_args = parser.parse_args()
    raw_source_dir = parsed_args.source[0]
    source_dir = Path(raw_source_dir).absolute()
    if not source_dir.is_dir():
        raise ValueError("Not a directory: " + str(source_dir))

    if maybe_target_dir := parsed_args.target:
        raw_target_dir = maybe_target_dir[0]
        target_dir = Path(raw_target_dir).absolute()
        if not target_dir.is_dir():
            raise ValueError("Not a directory: " + str(target_dir))
    else:
        target_dir = source_dir

    if maybe_source_suffix := parsed_args.source_file_suffix:
        source_suffix = maybe_source_suffix[0]
        if not source_suffix.startswith("."):
            raise ValueError(f"Suffix does not start with '.': {source_suffix}")
    else:
        source_suffix = None

    if maybe_target_suffix := parsed_args.target_file_suffix:
        target_suffix = maybe_target_suffix[0]
        if not target_suffix.startswith("."):
            raise ValueError(f"Suffix does not start with '.': {target_suffix}")
    else:
        target_suffix = None

    return AschenputtelArgs(
        source_dir, target_dir, source_suffix, target_suffix, parsed_args.dry_run
    )


def validate_args(args: AschenputtelArgs) -> None:
    if not args.target and not args.source_suffix and not args.target_suffix:
        raise ArgumentError(
            target_action, "Nothing to do. Either define a target directory or suffixes"
        )

    if args.source_suffix and not args.target_suffix:
        raise ArgumentError(
            target_suffix_action,
            "If --source-suffix is defined --target-suffix has to be defined",
        )
    elif args.target_suffix and not args.source_suffix:
        raise ArgumentError(
            source_suffix_action,
            "If --target-suffix is defined --source-suffix has to be defined",
        )


def gather(p: Path, suffix: str | None = None) -> dict[Path, Path]:
    all_files = [(path, dirnames, filenames) for path, dirnames, filenames in p.walk()]
    relative2absolute = {}
    current_absolute: Path
    current_relative: Path
    if suffix:
        suffix = suffix.lower()
    for pathname, dirnames, filenames in all_files:
        for name in filenames:
            if suffix and not name.lower().endswith(suffix):
                continue

            current_absolute = Path(pathname, name)
            current_relative = current_absolute.relative_to(p)
            if suffix:
                current_relative = current_relative.with_suffix("")
            relative2absolute[current_relative] = current_absolute
    return relative2absolute


def diff_from_target(
    relative2absolute_source: dict[Path, Path],
    relative2absolute_target: dict[Path, Path],
) -> list[Path]:
    relative_source = relative2absolute_source.keys()
    relative_target = relative2absolute_target.keys()

    diff_relative = relative_target - relative_source
    return [relative2absolute_target[relative] for relative in diff_relative]


def get_to_delete(
    source: Path, source_suffix: str | None, target: Path, target_suffix: str | None
) -> list[Path]:
    relative2absolute_s = gather(source, source_suffix)
    relative2absolute_t = gather(target, target_suffix)

    return diff_from_target(relative2absolute_s, relative2absolute_t)


if __name__ == "__main__":
    args = extract_args()
    validate_args(args)

    to_delete = get_to_delete(
        args.source, args.source_suffix, args.target, args.target_suffix
    )
    for file in to_delete:
        print(f"Deleting {file}...")
        if not args.dry_run:
            os.remove(file)
