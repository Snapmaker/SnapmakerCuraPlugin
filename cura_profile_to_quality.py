import logging
import os.path
import sys
import zipfile
from pathlib import Path

from _private.Profile import Profile


def print_usage():
    print("Import Cura profile to create a new quality:")
    print("Usage:")
    print("python cura_profile_to_quality.py {cura profile file}")


def import_profile(profile_path: Path) -> None:
    if not os.path.exists(profile_path):
        print("profile file %s doesn't exists!" % profile_path)
        return

    # parse curaprofile as zip file
    new_profile = Profile("New Profile")
    new_profile.set_name("New Profile")
    new_profile.set_definition("snapmaker_j1")

    with zipfile.ZipFile(profile_path, "r") as archive:
        for profile_id in archive.namelist():
            with archive.open(profile_id) as f:
                serialized_bytes = f.read()
                serialized = serialized_bytes.decode("utf-8")

            profile = Profile(profile_id)
            profile.deserialize(serialized)

            new_profile.set_from_profile(profile)

            # write to file for debugging
            filename = profile_id if profile_id.endswith(".inst.cfg") else "{}.inst.cfg".format(profile_id)
            with open(filename, "w") as f:
                f.write(serialized)

    new_profile.validate_general()
    new_profile.validate_metadata()
    new_profile.validate_values()

    output_path = Path("output.inst.cfg")
    with open(output_path, "w") as f:
        serialized = new_profile.serialize()
        f.write(serialized)


def main():
    if len(sys.argv) < 2:
        print_usage()
        sys.exit(0)

    profile_path = Path(sys.argv[1]).absolute()

    logging.basicConfig(level=logging.DEBUG)
    logging.info("Checking cura profile: %s" % profile_path)

    import_profile(profile_path)


if __name__ == '__main__':
    main()
