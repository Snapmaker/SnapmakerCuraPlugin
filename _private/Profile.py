import io
from typing import Dict
import logging
from configparser import ConfigParser
from collections import OrderedDict

from .quality_defs import QUALITY_KEYS, EXTRUDER_QUALITY_KEYS, IGNORED_QUALITY_KEYS


class InvalidProfileException(Exception):
    pass


class Profile:

    def __init__(self, profile_id: str) -> None:
        self.profile_id = profile_id
        self._name = ""
        self._definition = ""
        self._metadata = {}  # type: Dict[str, str]
        self._values = {}  # type: Dict[str, str]
        self._is_global = True

    def set_name(self, name: str) -> None:
        self._name = name

    def set_definition(self, definition: str) -> None:
        self._definition = definition

    def set_global(self, is_global: bool) -> None:
        self._is_global = is_global

    @property
    def metadata(self) -> Dict[str, str]:
        return self._metadata

    @property
    def values(self) -> Dict[str, str]:
        return self._values

    def __parse_general(self, parser: ConfigParser) -> None:
        """

        Example:
          [general]
          version = 4
          name = ...
          definition =
        """
        if not parser.has_section("general"):
            raise InvalidProfileException("Missing section 'general'")

        version = parser["general"]["version"]  # we assume that version is latest
        name = parser["general"]["name"]
        definition = parser["general"]["definition"]

        print("---------- Read profile %s ----------" % name)
        print(" * version = %s" % version)
        print(" * definition = %s" % definition)
        self._name = name
        self._definition = definition

    def __parse_metadata(self, parser: ConfigParser) -> None:
        """

        Example:
          [metadata]
          type = quality_changes
          quality_type = draft
          setting_version = 19
        """
        if not parser.has_section("metadata"):
            raise InvalidProfileException("Missing section 'metadata'")

        section = parser["metadata"]

        metadata = {
            "setting_version": section["setting_version"],
            "type": section["type"],
            "quality_type": section["quality_type"],
            "global_quality": section.get("global_quality", "False"),
            "weight": section.get("weight", "0"),
        }

        if parser.has_option("metadata", "position"):
            # it's a extruder profile
            position = parser["metadata"]["position"]
            print("Parsing extruder profile (position = %s)..." % position)
            metadata["position"] = position
        else:
            print("Parsing global profile...")

        if parser.has_option("metadata", "material"):
            metadata["material"] = parser["metadata"]["material"]

        self._metadata.update(metadata)

        print(" * metadata = {}".format(self._metadata))

    def __parse_values(self, parser: ConfigParser) -> None:
        if not parser.has_section("values"):
            raise InvalidProfileException("Missing section 'value'")

        print(" * values =")
        for key, value in parser["values"].items():
            # value = parser["values"][key]
            self._values[key] = value
            print(" " * 4, "{} = {}".format(key, value))

    def deserialize(self, serialized: str) -> None:
        parser = ConfigParser(interpolation=None)
        parser.read_string(serialized)

        self.__parse_general(parser)
        self.__parse_metadata(parser)
        self.__parse_values(parser)

    def serialize(self) -> str:
        parser = ConfigParser(interpolation=None, dict_type=OrderedDict)

        # general
        parser.add_section("general")
        parser.set("general", "name", self._name)
        parser.set("general", "version", "4")
        parser.set("general", "definition", self._definition)

        # metadata
        parser.add_section("metadata")
        for key, value in self._metadata.items():
            parser.set("metadata", key, value)

        # values
        parser.add_section("values")
        value_section = parser["values"]

        keys = QUALITY_KEYS if self._is_global else EXTRUDER_QUALITY_KEYS

        for key in keys:
            if key in self._values:
                value = self._values[key]
                value_section[key] = value

        # order
        parser._sections["values"] = OrderedDict(sorted(value_section.items(), key=lambda item: item[0]))

        output = io.StringIO()
        parser.write(output)
        return output.getvalue()

    def set_from_profile(self, profile: "Profile") -> None:
        """Set/Combine from another profile."""
        if not self._metadata:
            self._metadata.update(profile.metadata)

        for key, value in profile.values.items():
            if key in IGNORED_QUALITY_KEYS:
                continue

            # limit for not global keys
            if not self._is_global and key not in EXTRUDER_QUALITY_KEYS:
                continue

            if key not in self._values:
                self._values[key] = value
            else:
                if self._values[key] != value:
                    logging.warning("Value Conflicts: %s = %s / %s (using %s)", key, self._values[key], value,
                                    self._values[key])

    def validate_general(self) -> None:
        if not self._name:
            raise InvalidProfileException("No name set.")
        if not self._definition:
            raise InvalidProfileException("No definition set.")

    def validate_metadata(self) -> None:
        if self._metadata.get("setting_version", "1") != "20":
            self._metadata["setting_version"] = "20"

        # if not it's not global, remove it
        # if self._metadata.get("global_quality", "False") == "False":  # export only if it's true
        #    del self._metadata["global_quality"]

        if self._metadata["type"] != "quality":  # fix quality_changes (exported) to quality
            logging.warning("profile type = %s, changing it to \"quality\"." % self._metadata["type"])
            self._metadata["type"] = "quality"
