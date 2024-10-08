import re
import flexidict
import ast
from ament_index_python.packages import get_package_share_directory

# Global variables
current_properties = dict(default=dict(variables=dict(), functions=dict()))
current_local_key_list = []

# Persistent eval_globals dictionary

def print_properties():
    YELLOW = "\033[33m"
    RESET = "\033[0m"  # Reset color to default
    print(f'{YELLOW}print_properties:{RESET} {current_properties}')

eval_globals = {"__builtins__": __builtins__, "print_properties": print_properties,    "get_package_share_directory": get_package_share_directory}

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

        # After execution, update properties with new variables
        if is_assignment:
            new_vars = set(eval_globals.keys()) - set(old_eval_globals.keys())
            for var_name in new_vars:
                var_value = eval_globals[var_name]
                # Convert var_value back to string for storage
                var_value_str = repr(var_value)
                properties['default']['variables'][var_name] = {'value': var_value_str, 'scope': 'local'}
                # Add the variable name to the local_key_list
                if var_name not in local_key_list:
                    local_key_list.append(var_name)

        result += str(evaluated)
        last_idx = end

    result += value[last_idx:]
    return result



def AA():
    return 'hello world'


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
    current_local_key_list = []

    process(f'$(a="drone")')

    print(process(f'$(AA())'))

    print(process(f'$(get_package_share_directory(a))'))
    print(process(f'$(math.pi)'))
    # print(process('using dict format: $(t = {"a": 1, "b": 2, "c": 3})'))
    w = str(process('$(dict(a=1, b=2, c=3))'))
    print(process(f"$(t = {w})"))

    # print(process('using dict format: $(t = dict(a=1, b=2, c=3))'))
    print(process('t["b"] = $(t["b"])'))
    print(process(f'$(x+y)'))