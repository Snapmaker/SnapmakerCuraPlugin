import logging
import os.path

from _private.Profile import Profile
from _private.parameters import ParameterDefinitions
from _private.validate_parameters import validate_global_quality_values, validate_extruder_quality_values


def get_parameter_definitions() -> ParameterDefinitions:
    logging.info("Reading fdmprinter.def.json")
    definition_file_path = os.path.join("resources", "fdmprinter.def.json")
    definition_file_path = os.path.abspath(definition_file_path)
    parameter_definitions = ParameterDefinitions()
    with open(definition_file_path, "r") as f:
        serialized = f.read()
        parameter_definitions.deserialize(serialized)

    return parameter_definitions

def check_quality_dir(quality_dir: str) -> None:
    for filename in os.listdir(quality_dir):
        quality_path = os.path.join(quality_dir, filename)

        logging.info("Processing quality file: %s", quality_path)
        with open(quality_path, "r") as f:
            serialized = f.read()

        profile = Profile("Unknown")
        profile.deserialize(serialized)

        is_global_quality = profile.metadata["global_quality"] == "True"
        if is_global_quality:
            profile.set_global(True)
            validate_global_quality_values(profile)
        else:
            profile.set_global(False)
            validate_extruder_quality_values(profile)

        # write it back
        with open(quality_path, "w") as f:
            serialized = profile.serialize()
            f.write(serialized)


def main():
    logging.basicConfig(level=logging.DEBUG)
    logging.info("Checking quality files...")

    parameter_definitions = get_parameter_definitions()
    logging.info("%s parameters in total", len(parameter_definitions.parameters))

    logging.info("Checking Snapmaker J1...")

    plugin_profile_root_dir = os.path.join("resources", "snapmaker_j1_profiles")
    plugin_profile_root_dir = os.path.abspath(plugin_profile_root_dir)
    plugin_quality_dir = os.path.join(plugin_profile_root_dir, "quality", "snapmaker_j1")

    check_quality_dir(plugin_quality_dir)

    logging.info("Checking Snapmaker Artisan...")

    plugin_profile_root_dir = os.path.join("resources", "snapmaker_artisan")
    plugin_profile_root_dir = os.path.abspath(plugin_profile_root_dir)
    plugin_quality_dir = os.path.join(plugin_profile_root_dir, "quality", "snapmaker_artisan")

    check_quality_dir(plugin_quality_dir)

    logging.info("Done.")


if __name__ == "__main__":
    main()
