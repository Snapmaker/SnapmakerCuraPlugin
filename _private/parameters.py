from typing import Dict, Any, List
import json
import collections


class Parameter:

    def __init__(self, key: str, ) -> None:
        self.key = key
        self.value = None
        self.settable_per_mesh = False
        self.settable_per_extruder = False
        # self.settable_per_meshgroup = False


class ParameterDefinitions:

    def __init__(self) -> None:
        self._parameters = {}

    @property
    def parameters(self) -> Dict[str, Parameter]:
        return self._parameters

    def __deserialize_item(self, key: str, parsed: Dict[str, Any]) -> None:
        parameter = Parameter(key)
        try:
            parameter.value = parsed["default_value"]
        except:
            # only one exception: Monotonic Top Surface Order
            parameter.value = parsed["value"]
            print(key, parsed)
        parameter.settable_per_mesh = parsed.get("settable_per_mesh", False)
        parameter.settable_per_extruder = parsed.get("settable_per_extruder", False)

        self._parameters[key] = parameter

        if parsed.get("children"):
            for key, value in parsed["children"].items():
                self.__deserialize_item(key, value)

    def __deserialize_category(self, parsed: Dict[str, Any]) -> None:
        for key, value in parsed["children"].items():
            self.__deserialize_item(key, value)

    def deserialize(self, serialized: str) -> None:
        parsed = json.loads(serialized, object_pairs_hook=collections.OrderedDict)

        for key, value in parsed["settings"].items():
            if value["type"] == "category":
                self.__deserialize_category(value)

    def get_parameter(self, key: str) -> None:
        return self._parameters[key]


