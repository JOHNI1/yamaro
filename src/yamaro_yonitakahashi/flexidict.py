# my_module.py
#
# Copyright (C) 2024 Yoni Takahashi
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <https://www.gnu.org/licenses

import yaml

import math



def flexidict_to_dict(flexidict_instance):
    """
    Converts a FlexiDict instance into a regular dictionary.
    In case of duplicate keys, the last occurrence will overwrite the earlier ones.
    """
    result_dict = {}

    # Iterate over the key-value pairs in the FlexiDict
    for key, value in flexidict_instance:
        if isinstance(value, FlexiDict):
            # Recursively convert nested FlexiDict to a regular dictionary
            result_dict[key] = flexidict_to_dict(value)
        else:
            # Overwrite any existing value for the same key
            result_dict[key] = value

    return result_dict




"""This class allows keys with the same name!"""
class FlexiDict:
    def __init__(self):
        self._items = []

    def add(self, key, value):
        """Add a key-value pair, allowing duplicates."""
        self._items.append([key, value])

    def keys(self):
        """Retrieve all values for a given key."""
        return [k[0] for k in self._items]
    
    def __len__(self):
        """Return the number of key-value pairs in the FlexiDict."""
        return len(self._items)

    def __getitem__(self, key):
        if not isinstance(key, str):
            return self._items[key]
        """Retrieve all values for a given key using dict-like syntax."""
        values = [v for k, v in self._items if k == key]
        if values:
            return values
        else:
            raise KeyError(key)
        

    def __iter__(self):
        """Iterate over the key-value pairs."""
        return iter(self._items)

    def __repr__(self):
        """String representation of FlexiDict."""
        return self._pretty_repr(indent_level=0)

    def _pretty_repr(self, indent_level):
        """Helper function for pretty-printing the FlexiDict."""
        indent = '  ' * indent_level
        result = '[\n'
        for key, value in self._items:
            result += f"{indent}  ['{key}', "
            if isinstance(value, FlexiDict):
                result += value._pretty_repr(indent_level + 1) + '],\n'
            elif isinstance(value, list) and not isinstance(value, str):
                if all(isinstance(item, (int, float, str)) for item in value):
                    result += repr(value) + '],\n'
                else:
                    result += '[\n'
                    for item in value:
                        result += f"{indent}    {repr(item)},\n"
                    result += f"{indent}  ]],\n"
            else:
                result += repr(value) + '],\n'
        result += indent + ']'
        return result

# Custom constructor for mappings
def construct_flexidict(loader, node):
    flexidict = FlexiDict()
    # Process key-value pairs
    for key_node, value_node in node.value:
        key = loader.construct_object(key_node)
        value = loader.construct_object(value_node)
        flexidict.add(key, value)
    return flexidict

# Custom Loader that uses the FlexiDict constructor
class FlexiLoader(yaml.SafeLoader):
    pass

FlexiLoader.add_constructor(
    yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, construct_flexidict
)

# Now, when we load the YAML using FlexiLoader, mappings will be constructed as FlexiDict, and duplicate keys will be preserved.



#make sure that later, the path is not self because that will cause infinite recursion!!!!
def load_yaml_to_FlexiDict(yaml_file_path):
    with open(yaml_file_path, 'r') as f:
        return yaml.load(f, Loader=FlexiLoader)



if __name__ == "__main__":
    t = load_yaml_to_FlexiDict('drone.yaml')
    print(t)
    print()
    # print(type(t))
    # print(type(t['variables'][0]))
    # print(type(t['variables'][0]["A"]))
    print(flexidict_to_dict(t))

