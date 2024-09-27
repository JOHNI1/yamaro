import yaml


"""This class allows keys with the same name!"""
class FlexiDict:
    def __init__(self):
        self._items = []

    def add(self, key, value):
        """Add a key-value pair, allowing duplicates."""
        self._items.append([key, value])

    def key_values(self, key):
        """Retrieve all values for a given key."""
        return [v for k, v in self._items if k == key]

    def __getitem__(self, key):
        """Retrieve all values for a given key using dict-like syntax."""
        values = self.key_values(key)
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
