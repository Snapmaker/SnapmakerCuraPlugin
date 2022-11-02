import logging
import os.path
import sys
import zipfile
from pathlib import Path

from profile.Profile import Profile


def print_usage():
    print("Usage:")
    print("python scripts/import_curaprofile {cura profile file} {output folder}")


def import_profile(profile_path: Path, output_folder: Path) -> None:
    if not os.path.exists(profile_path):
        print("profile file %s doesn't exists!" % profile_path)
        return

    # parse curaprofile as zip file
    with zipfile.ZipFile(profile_path, "r") as archive:
        for profile_id in archive.namelist():
            with archive.open(profile_id) as f:
                serialized_bytes = f.read()
                serialized = serialized_bytes.decode("utf-8")

            profile = Profile(profile_id)
            profile.deserialize(serialized)

            output_path = Path(output_folder, profile_id + ".inst.cfg")
            with open(output_path, "w") as f:
                f.write(serialized)


def main():
    if len(sys.argv) < 3:
        print_usage()
        sys.exit(0)

    profile_path = Path(sys.argv[1]).absolute()
    output_folder = Path(sys.argv[2]).absolute()

    logging.basicConfig(level=logging.DEBUG)
    logging.info("Checking cura profile: %s" % profile_path)

    import_profile(profile_path, output_folder)


if __name__ == '__main__':
    main()
