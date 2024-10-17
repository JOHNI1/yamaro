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

def pretty_print_dict(d, indent_level=0):
    """Recursively pretty-prints a nested dictionary."""
    indent = '  ' * indent_level
    result = '{\n'
    
    for key, value in d.items():
        result += f"{indent}  '{key}': "
        
        if isinstance(value, dict):
            result += pretty_print_dict(value, indent_level + 1) + ',\n'
        elif isinstance(value, list) and not isinstance(value, str):
            result += '[\n'
            for item in value:
                result += f"{indent}    {repr(item)},\n"
            result += f"{indent}  ],\n"
        else:
            result += repr(value) + ',\n'
    
    result += indent + '}'
    return result



if __name__ == '__main__':
    # Example Usage
    data = {
        'default': {
            'functions': {},
            'variables': {
                'A': {'value': [30, 120, 210, 300], 'scope': 'global'},
                'B': {'value': {'x': 1, 'y': 2}, 'scope': 'parent'},
                'C': {'value': 'hiii', 'scope': 'child'},
                'D': {'value': [10, 20, 30, 40], 'scope': 'local'}
            }
        }
    }

    print(pretty_print_dict(data))
