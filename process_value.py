import re
import flexidict



def process_value(string, properties):
    # Ensure that the input is processed only if it's a string
    if not isinstance(string, str):
        if isinstance(string, flexidict.FlexiDict):
            string = flexidict.flexidict_to_dict(string)  # Convert FlexiDict to regular dict
        if isinstance(string, list):
            for i in range(len(string)):
                string[i] = process_value(string[i], properties)
            return string  # Ensure to return the processed list here
        elif isinstance(string, dict):
            for key in list(string.keys()):
                string[key] = process_value(string[key], properties)
            return string  # Return processed dictionary
        elif isinstance(string, set):
            string = {process_value(item, properties) for item in string}
            return string  # Return processed set
        else:
            return string  # If it's another type, just return it

    # Only process the expressions if it's a string
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

    # Process the string if it's an actual string with expressions
    expressions = find_expressions(string)
    result = ''
    last_idx = 0

    for start, end, expr in expressions:
        result += string[last_idx:start]

        local_vars = {}

        # Populate the local_vars from 'default' namespace
        for var_name, var_info in properties['default']['variables'].items():
            local_vars[var_name] = var_info['value']

        def replace_variables(expression):
            for ns_key, ns_value in properties.items():
                if ns_key == 'default':
                    continue
                for var_name, var_info in ns_value['variables'].items():
                    # Look for the pattern 'namespace.variable'
                    var_pattern = r'\b' + re.escape(ns_key) + r'\.' + re.escape(var_name) + r'\b'
                    if re.search(var_pattern, expression):
                        # Ensure read-only access by not modifying properties inside the namespace
                        var_value = var_info['value']
                        expression = re.sub(var_pattern, repr(var_value), expression)
            return expression

        expr_with_vars = replace_variables(expr)

        # Handle variable assignment only for default scope
        is_assignment = '=' in expr_with_vars
        if is_assignment and '.' in expr_with_vars.split('=')[0]:
            # Disallow assignment in any namespace except 'default'
            raise RuntimeError(f"Cannot assign in namespaces: {expr_with_vars}")

        # Execute the expression
        try:
            if is_assignment:
                exec(expr_with_vars, {}, local_vars)
                for var_name in local_vars:
                    properties['default']['variables'][var_name] = {'value': local_vars[var_name], 'scope': 'local'}
                evaluated = ''
            else:
                evaluated = str(eval(expr_with_vars, {}, local_vars))
        except Exception as e:
            raise RuntimeError(f"Error evaluating expression '{expr_with_vars}': {e}")

        result += evaluated
        last_idx = end

    result += string[last_idx:]
    return result



# # '''the properties is not a copy but pointer that's why eval works in here'''
# # def process_value(string, properties):
# #     if not isinstance(string, str):
# #         if isinstance(string, flexidict.FlexiDict):
# #             string = flexidict.flexidict_to_dict(string) #sorry but I only allow dict data structure. no FlexiDict please!
# #         if isinstance(string, list):
# #             for i in range(len(string)):
# #                 string[i] = process_value(string[i], properties)
# #         elif isinstance(string, dict):
# #             for key in list(string.keys()):
# #                 string[key] = process_value(string[key], properties)
# #         elif isinstance(string, set):
# #             string = {process_value(item, properties) for item in string}
# #         else:
# #             return string


# #     # Function to find all occurrences of $(...) in the string,
# #     # correctly handling nested parentheses
# #     def find_expressions(s):
# #         expressions = []
# #         idx = 0
# #         while idx < len(s):
# #             if s[idx:idx+2] == '$(':
# #                 start_idx = idx + 2
# #                 idx = start_idx
# #                 stack = 1  # We have one '(' from '$('
# #                 while idx < len(s) and stack > 0:
# #                     if s[idx] == '(':
# #                         stack += 1
# #                     elif s[idx] == ')':
# #                         stack -= 1
# #                     idx += 1
# #                 if stack == 0:
# #                     end_idx = idx
# #                     expr = s[start_idx:idx-1]
# #                     expressions.append((start_idx - 2, end_idx, expr))
# #                 else:
# #                     raise ValueError("Unmatched '(' in string")
# #             else:
# #                 idx += 1
# #         return expressions

# #     # Get the expressions and their positions
# #     expressions = find_expressions(string)

# #     # Initialize the result string
# #     result = ''
# #     last_idx = 0
# #     for start, end, expr in expressions:
# #         # Append the part of the string before the expression
# #         result += string[last_idx:start]

# #         # Prepare the local context for exec/eval
# #         local_vars = {}
# #         # Add existing variables to local_vars
# #         for var_name, var_info in properties['default']['variables'].items():
# #             local_vars[var_name] = var_info['value']

# #         # Replace variables in expr
# #         def replace_variables(expression):
# #             # Match variables that are not preceded or followed by word characters
# #             for var_name in properties['default']['variables']:
# #                 var_pattern = r'(?<!\w)' + re.escape(var_name) + r'(?!\w)'
# #                 var_value = var_name  # Keep the variable name as is
# #                 expression = re.sub(var_pattern, var_value, expression)
# #             return expression

# #         expr_with_vars = replace_variables(expr)

# #         # Determine if the expression is an assignment
# #         is_assignment = '=' in expr_with_vars

# #         # Execute the expression
# #         try:
# #             if is_assignment:
# #                 exec(expr_with_vars, {}, local_vars)
# #                 # Update properties with new or modified variables
# #                 for var_name in local_vars:
# #                     properties['default']['variables'][var_name] = {'value': local_vars[var_name], 'scope': 'local'}
# #                 evaluated = ''  # Assignments don't produce output
# #             else:
# #                 evaluated = str(eval(expr_with_vars, {}, local_vars))
# #         except Exception as e:
# #             raise RuntimeError(f"Error evaluating expression '{expr_with_vars}': {e}")

# #         # Append the evaluated result (or empty string) to the result
# #         result += evaluated
# #         last_idx = end

# #     # Append any remaining part of the string
# #     result += string[last_idx:]

# #     return result


if __name__ == "__main__":
    # Example usage
    properties = {
        'default': {
            'functions': {},
            'variables': {
                'a': {'value': '10', 'scope': 'local'},   # String value
                'b': {'value': 1, 'scope': 'child'},      # Integer value
                't': {'value': 2, 'scope': 'parent'},     # Integer value
                'd': {'value': 4, 'scope': 'global'}      # Integer value
            }
        },
        'controller': {
            'functions': {},
            'variables': {
                'a': {'value': '3', 'scope': 'local'},     # String value
                'b': {'value': 0, 'scope': 'child'},       # Integer value
                't': {'value': -1, 'scope': 'parent'},     # Integer value
                'd': {'value': -2, 'scope': 'global'},      # Integer value
                'w': {'value': dict(a=dict(a='10', b=dict(a='10', b=1, t=dict(a='10', b=1, t=2, d=4), d=4), t=2, d=4), b=1, t=2, d=4), 'scope': 'local'}
            }
        }
    }



    # Test case with an assignment
    # string = "link_$(w=dict(a=dict(a='10', b=dict(a='10', b=1, t=dict(a='10', b=1, t=2, d=4), d=4), t=2, d=4), b=1, t=2, d=4))"
    # result = process_value(string, properties)

    # string = "link_$(pow(3, (int(w['a']['b']['t']['a'])+int(a))%3))"
    string = "link_$(int(a))"
    result = process_value(string, properties)
    print(result)  # Expected output: 'link_'

    # Verify that 'k' is now in properties
    print("Updated properties:", properties['default']['variables'])

    # Test case with an assignment

    # string = "link_$(pow(3, (int(controller.w['a']['b']['t']['a'])+int(controller.a))%3))"
    string = "link_$(int(controller.a))"
    result = process_value(string, properties)
    print(result)  # Expected output: 'link_'

