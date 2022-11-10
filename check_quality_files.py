import logging
import os.path

from _private.parameters import ParameterDefinitions


def main():
    logging.basicConfig(level=logging.DEBUG)
    logging.info("Checking quality files...")

    logging.info("Reading fdmprinter.def.json")
    definition_file_path = os.path.join("resources", "fdmprinter.def.json")
    definition_file_path = os.path.abspath(definition_file_path)
    parameter_definitions = ParameterDefinitions()
    with open(definition_file_path, "r") as f:
        serialized = f.read()
        parameter_definitions.deserialize(serialized)
    logging.info("%s parameters in total", len(parameter_definitions.parameters))

    plugin_profile_root_dir = os.path.join("resources", "snapmaker_j1_profiles")
    plugin_profile_root_dir = os.path.abspath(plugin_profile_root_dir)
    plugin_quality_dir = os.path.join(plugin_profile_root_dir, "quality", "snapmaker_j1")

    for filename in os.listdir(plugin_quality_dir):
        print(filename)
        with open(filename, "r") as f:
            serialized = f.read()
            profile = Profile("Unknown")
            

    logging.info("Done.")


if __name__ == "__main__":
    main()
