import re
import flexidict




'''the properties is not a copy but pointer that's why eval works in here'''
def process_value(string, properties):
    if not isinstance(string, str):
        if isinstance(string, flexidict.FlexiDict):
            string = flexidict.flexidict_to_dict(string) #sorry but I only allow dict data structure. no FlexiDict please!
        if isinstance(string, list):
            for i in range(len(string)):
                string[i] = process_value(string[i], properties)
        elif isinstance(string, dict):
            for key in list(string.keys()):
                string[key] = process_value(string[key], properties)
        elif isinstance(string, set):
            string = {process_value(item, properties) for item in string}
        else:
            return string


    # Function to find all occurrences of $(...) in the string,
    # correctly handling nested parentheses
    def find_expressions(s):
        expressions = []
        idx = 0
        while idx < len(s):
            if s[idx:idx+2] == '$(':
                start_idx = idx + 2
                idx = start_idx
                stack = 1  # We have one '(' from '$('
                while idx < len(s) and stack > 0:
                    if s[idx] == '(':
                        stack += 1
                    elif s[idx] == ')':
                        stack -= 1
                    idx += 1
                if stack == 0:
                    end_idx = idx
                    expr = s[start_idx:idx-1]
                    expressions.append((start_idx - 2, end_idx, expr))
                else:
                    raise ValueError("Unmatched '(' in string")
            else:
                idx += 1
        return expressions

    # Get the expressions and their positions
    expressions = find_expressions(string)

    # Initialize the result string
    result = ''
    last_idx = 0
    for start, end, expr in expressions:
        # Append the part of the string before the expression
        result += string[last_idx:start]

        # Prepare the local context for exec/eval
        local_vars = {}
        # Add existing variables to local_vars
        for var_name, var_info in properties['default']['variables'].items():
            local_vars[var_name] = var_info['value']

        # Replace variables in expr
        def replace_variables(expression):
            # Match variables that are not preceded or followed by word characters
            for var_name in properties['default']['variables']:
                var_pattern = r'(?<!\w)' + re.escape(var_name) + r'(?!\w)'
                var_value = var_name  # Keep the variable name as is
                expression = re.sub(var_pattern, var_value, expression)
            return expression

        expr_with_vars = replace_variables(expr)

        # Determine if the expression is an assignment
        is_assignment = '=' in expr_with_vars

        # Execute the expression
        try:
            if is_assignment:
                exec(expr_with_vars, {}, local_vars)
                # Update properties with new or modified variables
                for var_name in local_vars:
                    properties['default']['variables'][var_name] = {'value': local_vars[var_name], 'scope': 'local'}
                evaluated = ''  # Assignments don't produce output
            else:
                evaluated = str(eval(expr_with_vars, {}, local_vars))
        except Exception as e:
            raise RuntimeError(f"Error evaluating expression '{expr_with_vars}': {e}")

        # Append the evaluated result (or empty string) to the result
        result += evaluated
        last_idx = end

    # Append any remaining part of the string
    result += string[last_idx:]

    return result



# Example usage
properties = {
    'default': {
        'functions': {},
        'variables': {
            'a': {'value': '10', 'scope': 'parent'},  # String value
            'b': {'value': 1, 'scope': 'global'},     # Integer value
            't': {'value': 2, 'scope': 'parent'},     # Integer value
            'd': {'value': 4, 'scope': 'global'}      # Integer value
        }
    }
}



# Test case with an assignment
string = "link_$(w=dict(a=dict(a='10', b=dict(a='10', b=1, t=dict(a='10', b=1, t=2, d=4), d=4), t=2, d=4), b=1, t=2, d=4))"
result = process_value(string, properties)

string = "link_$(pow(10, (int(w['a']['b']['t']['a'])**int(a))%10))"
result = process_value(string, properties)
print(result)  # Expected output: 'link_'

# Verify that 'k' is now in properties
print("Updated properties:", properties['default']['variables'])
