import logging

from _private.Profile import Profile, InvalidProfileException
from _private.quality_defs import IGNORED_QUALITY_KEYS, QUALITY_KEYS,  EXTRUDER_QUALITY_KEYS


def validate_global_quality_values(profile: Profile) -> None:
    # check for existing values
    old_keys = list(profile.values.keys())
    for key in old_keys:
        # ignore some keys
        if key in IGNORED_QUALITY_KEYS:
            # logging.warning("Ignoring value %s (=%s)" % (key, value))
            continue

        # key shoule be defined in standard keys
        if key not in QUALITY_KEYS:
            logging.warning("key {} isn't allowed.".format(key))

            del profile.values[key]

    # if has_error and error_msg:
    #     raise InvalidProfileException(error_msg)

    keys = set(profile.values.keys())

    # check all keys are specified
    for key in QUALITY_KEYS:
        if key not in keys:
            logging.warning("key {} is missing in profile".format(key))
            raise InvalidProfileException()


def validate_extruder_quality_values(profile: Profile) -> None:
    # check for existing values
    old_keys = list(profile.values.keys())
    for key in old_keys:
        # ignore some keys
        if key in IGNORED_QUALITY_KEYS:
            # logging.warning("Ignoring value %s (=%s)" % (key, value))
            continue

        # key shoule be defined in standard keys
        if key not in EXTRUDER_QUALITY_KEYS:
            logging.warning("key {} isn't allowed.".format(key))

            del profile.values[key]

    # if has_error and error_msg:
    #     raise InvalidProfileException(error_msg)

    keys = set(profile.values.keys())

    # check all keys are specified
    for key in EXTRUDER_QUALITY_KEYS:
        if key not in keys:
            logging.warning("key {} is missing in profile".format(key))
            raise InvalidProfileException()
