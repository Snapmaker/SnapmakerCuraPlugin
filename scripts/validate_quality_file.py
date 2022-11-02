import sys
import os
import logging
from pathlib import Path

from profile.Profile import Profile


def print_usage():
    print("Usage:")
    print("python scripts/validate_quality_file {quality file}")


def validate(quality_file: Path) -> None:
    if not os.path.exists(quality_file):
        print("quality file doesn't exists!" % quality_file)
        return

    with open(quality_file, "r") as f:
        serialized = f.read()

    profile = Profile(quality_file.name)
    profile.deserialize(serialized)

    profile.validate_general()
    profile.validate_metadata()
    profile.validate_values()

    serialized = profile.serialize()
    with open(quality_file, "w") as f:
        f.write(serialized)


def main():
    if len(sys.argv) < 2:
        print_usage()
        sys.exit(0)

    quality_file = Path(sys.argv[1]).absolute()

    logging.basicConfig(level=logging.DEBUG)
    logging.info("Validate quality file: %s" % quality_file)

    validate(quality_file)


if __name__ == '__main__':
    main()
