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

import re
import ast
from . import flexidict
from .pretty_print_dict import pretty_print_dict
# import flexidict
# from pretty_print_dict import pretty_print_dict


# Global variables
current_properties = dict(default=dict(variables=dict(), functions=dict()))
current_local_key_list = []

# Persistent eval_globals dictionary

def print_properties():
    YELLOW = "\033[33m"
    RESET = "\033[0m"  # Reset color to default
    print(f'{YELLOW}print_properties:{RESET} {pretty_print_dict(current_properties)}')


eval_globals = {"__builtins__": __builtins__, "print_properties": print_properties}

def process(value) -> str:
    global current_properties, current_local_key_list
    return process_value(value, current_properties, current_local_key_list)

def auto_convert(value_str):
    """
    Convert the string representation of a value to its original data type.
    """
    try:
        # Try to evaluate the string as a Python literal
        return ast.literal_eval(value_str)
    except (ValueError, SyntaxError):
        # If it's not a literal, return the original string
        return value_str

def process_value(value, properties, local_key_list) -> str:
    global eval_globals  # Use the persistent eval_globals
    # Process non-string values recursively
    if not isinstance(value, str):
        if isinstance(value, flexidict.FlexiDict):
            value = flexidict.flexidict_to_dict(value)
        if isinstance(value, list):
            for i in range(len(value)):
                value[i] = process_value(value[i], properties, local_key_list)
            return value
        elif isinstance(value, dict):
            for key in list(value.keys()):
                value[key] = process_value(value[key], properties, local_key_list)
            return value
        elif isinstance(value, set):
            value = {process_value(item, properties, local_key_list) for item in value}
            return value
        else:
            return value

    # Function to find expressions in the string
    def find_expressions(s):
        expressions = []
        idx = 0
        while idx < len(s):
            if s[idx:idx + 2] == '$(':
                start_idx = idx + 2
                idx = start_idx
                stack = 1  # One '(' from '$('
                while idx < len(s) and stack > 0:
                    if s[idx] == '(':
                        stack += 1
                    elif s[idx] == ')':
                        stack -= 1
                    idx += 1
                if stack == 0:
                    end_idx = idx
                    expr = s[start_idx:idx - 1]
                    expressions.append((start_idx - 2, end_idx, expr))
                else:
                    raise ValueError("Unmatched '(' in string")
            else:
                idx += 1
        return expressions

    # Process the string if it contains expressions
    expressions = find_expressions(value)
    result = ''
    last_idx = 0

    for start, end, expr in expressions:
        result += value[last_idx:start]

        # Remove local_vars and use eval_globals directly
        # local_vars = {}

        # Populate eval_globals with variables from properties
        for var_name, var_info in properties['default']['variables'].items():
            var_value = var_info['value']
            if isinstance(var_value, str):
                var_value = auto_convert(var_value)
            eval_globals[var_name] = var_value

        def replace_variables(expression):
            # Replace namespace variables in the expression
            for ns_key, ns_value in properties.items():
                if ns_key == 'default':
                    continue
                for var_name, var_info in ns_value['variables'].items():
                    var_pattern = r'\b' + re.escape(ns_key) + r'\.' + re.escape(var_name) + r'\b'
                    if re.search(var_pattern, expression):
                        var_value = var_info['value']
                        if isinstance(var_value, str):
                            var_value = auto_convert(var_value)
                        expression = re.sub(var_pattern, repr(var_value), expression)
            return expression

        expr_with_vars = replace_variables(expr)

        # Detect assignment or import statements
        is_assignment = re.match(r'^\s*[a-zA-Z_][a-zA-Z0-9_]*\s*=.*', expr_with_vars.strip()) is not None
        is_import = expr_with_vars.strip().startswith('import ')

        # Save a copy of eval_globals before execution
        old_eval_globals = eval_globals.copy()

        # Execute the expression
        try:
            if is_assignment or is_import:
                exec(expr_with_vars, eval_globals)
                evaluated = ''
            else:
                evaluated = eval(expr_with_vars, eval_globals)
        except Exception as e:
            raise RuntimeError(f"Error evaluating expression '{expr_with_vars}': {e}")

        # After execution, update properties with new or existing variables
        if is_assignment:
            for var_name in eval_globals.keys():
                if var_name in old_eval_globals and old_eval_globals[var_name] == eval_globals[var_name]:
                    continue  # Skip if the value hasn't changed

                # Add the variable name to the local_key_list only if it's not in current_properties
                if var_name not in properties['default']['variables'].keys():
                    if var_name in local_key_list:
                        raise Exception(f"something went wrong in process_value with local_key_list(yamaro's fault.). the variable defined in the expression {value} seems to be already in local_key_list but its not in current_properties.")
                    local_key_list.append(var_name)
                    
                var_value = eval_globals[var_name]
                # Convert var_value back to string for storage
                var_value_str = repr(var_value)

                if var_name in properties['default']['variables']:
                    # Update existing variable
                    properties['default']['variables'][var_name]['value'] = var_value_str
                else:
                    # Add new variable
                    properties['default']['variables'][var_name] = {'value': var_value_str, 'scope': 'local'}
                    


        result += str(evaluated)
        last_idx = end

    result += value[last_idx:]
    return result

if __name__ == "__main__":
    current_properties = {
        'default': {
            'variables': {
                'x': {'value': 10, 'scope': 'global'},
                'y': {'value': 20, 'scope': 'local'}
            }
        },
        'namespace1': {
            'variables': {
                'y': {'value': 20, 'scope': 'local'}
            }
        }
    }
    process(f'$(import os)')
    process(f'$(print(os.path.expanduser("~/yamaro/tests/dronecopy.yaml")))')

# if __name__ == "__main__":
#     current_properties = {
#         'default': {
#             'variables': {
#                 'x': {'value': 10, 'scope': 'global'},
#                 'y': {'value': 20, 'scope': 'local'}
#             }
#         },
#         'namespace1': {
#             'variables': {
#                 'y': {'value': 20, 'scope': 'local'}
#             }
#         }
#     }
#     process(f'$(a=10)')
#     del current_properties['default']['variables']['a']
#     process(f'$(print(a))')


# if __name__ == "__main__":
#     current_properties = {
#         'default': {
#             'variables': {
#                 'x': {'value': 10, 'scope': 'global'},
#                 'y': {'value': 20, 'scope': 'local'}
#             }
#         },
#         'namespace1': {
#             'variables': {
#                 'y': {'value': 20, 'scope': 'local'}
#             }
#         }
#     }
#     print(current_properties)
#     a = []
#     current_local_key_list = a
#     process(f'$(a=0)')
#     print(current_properties)
#     print('a:', a)

#     b = []
#     current_local_key_list = b
#     process(f'$(a=0)')
#     print(current_properties)
#     print('b:', b)

#     process(f'$(import os)')
#     print('hiiiiiii')

#     process(f'$(a=os.path.expanduser("~/yamaro/dronecopy.py"))')

#     print(process('$(a)'))


    
    # current_local_key_list = []

    # process(f'$(a="drone")')

    # print(process(f'$(AA())'))

    # print(process(f'$(get_package_share_directory(a))'))
    # print(process(f'$(math.pi)'))
    # # print(process('using dict format: $(t = {"a": 1, "b": 2, "c": 3})'))
    # w = str(process('$(dict(a=1, b=2, c=3))'))
    # print(process(f"$(t = {w})"))

    # # print(process('using dict format: $(t = dict(a=1, b=2, c=3))'))
    # print(process('t["b"] = $(t["b"])'))
    # print(process(f'$(x+y)'))