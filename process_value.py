# import re
# import flexidict
# # from ament_index_python.packages import get_package_share_directory


# def process_value(string, properties):
#     # Ensure that the input is processed only if it's a string
#     if not isinstance(string, str):
#         if isinstance(string, flexidict.FlexiDict):
#             string = flexidict.flexidict_to_dict(string)  # Convert FlexiDict to regular dict
#         if isinstance(string, list):
#             for i in range(len(string)):
#                 string[i] = process_value(string[i], properties)
#             return string  # Ensure to return the processed list here
#         elif isinstance(string, dict):
#             for key in list(string.keys()):
#                 string[key] = process_value(string[key], properties)
#             return string  # Return processed dictionary
#         elif isinstance(string, set):
#             string = {process_value(item, properties) for item in string}
#             return string  # Return processed set
#         else:
#             return string  # If it's another type, just return it

#     # Only process the expressions if it's a string
#     def find_expressions(s):
#         expressions = []
#         idx = 0
#         while idx < len(s):
#             if s[idx:idx + 2] == '$(':
#                 start_idx = idx + 2
#                 idx = start_idx
#                 stack = 1  # One '(' from '$('
#                 while idx < len(s) and stack > 0:
#                     if s[idx] == '(':
#                         stack += 1
#                     elif s[idx] == ')':
#                         stack -= 1
#                     idx += 1
#                 if stack == 0:
#                     end_idx = idx
#                     expr = s[start_idx:idx - 1]
#                     expressions.append((start_idx - 2, end_idx, expr))
#                 else:
#                     raise ValueError("Unmatched '(' in string")
#             else:
#                 idx += 1
#         return expressions

#     # Process the string if it's an actual string with expressions
#     expressions = find_expressions(string)
#     result = ''
#     last_idx = 0

#     for start, end, expr in expressions:
#         result += string[last_idx:start]

#         local_vars = {}

#         # Populate the local_vars from 'default' namespace
#         for var_name, var_info in properties['default']['variables'].items():
#             local_vars[var_name] = var_info['value']

#         def replace_variables(expression):
#             for ns_key, ns_value in properties.items():
#                 if ns_key == 'default':
#                     continue
#                 for var_name, var_info in ns_value['variables'].items():
#                     # Look for the pattern 'namespace.variable'
#                     var_pattern = r'\b' + re.escape(ns_key) + r'\.' + re.escape(var_name) + r'\b'
#                     if re.search(var_pattern, expression):
#                         # Ensure read-only access by not modifying properties inside the namespace
#                         var_value = var_info['value']
#                         expression = re.sub(var_pattern, repr(var_value), expression)
#             return expression

#         expr_with_vars = replace_variables(expr)

#         # Handle variable assignment only for default scope
#         is_assignment = '=' in expr_with_vars
#         if is_assignment and '.' in expr_with_vars.split('=')[0]:
#             # Disallow assignment in any namespace except 'default'
#             raise RuntimeError(f"Cannot assign in namespaces: {expr_with_vars}")

#         # Execute the expression
#         try:
#             if is_assignment:
#                 exec(expr_with_vars, {}, local_vars)
#                 for var_name in local_vars:
#                     properties['default']['variables'][var_name] = {'value': local_vars[var_name], 'scope': 'local'}
#                 evaluated = ''
#             else:
#                 evaluated = str(eval(expr_with_vars, {}, local_vars))
#         except Exception as e:
#             raise RuntimeError(f"Error evaluating expression '{expr_with_vars}': {e}")

#         result += evaluated
#         last_idx = end

#     result += string[last_idx:]
#     return result



# # # '''the properties is not a copy but pointer that's why eval works in here'''
# # # def process_value(string, properties):
# # #     if not isinstance(string, str):
# # #         if isinstance(string, flexidict.FlexiDict):
# # #             string = flexidict.flexidict_to_dict(string) #sorry but I only allow dict data structure. no FlexiDict please!
# # #         if isinstance(string, list):
# # #             for i in range(len(string)):
# # #                 string[i] = process_value(string[i], properties)
# # #         elif isinstance(string, dict):
# # #             for key in list(string.keys()):
# # #                 string[key] = process_value(string[key], properties)
# # #         elif isinstance(string, set):
# # #             string = {process_value(item, properties) for item in string}
# # #         else:
# # #             return string


# # #     # Function to find all occurrences of $(...) in the string,
# # #     # correctly handling nested parentheses
# # #     def find_expressions(s):
# # #         expressions = []
# # #         idx = 0
# # #         while idx < len(s):
# # #             if s[idx:idx+2] == '$(':
# # #                 start_idx = idx + 2
# # #                 idx = start_idx
# # #                 stack = 1  # We have one '(' from '$('
# # #                 while idx < len(s) and stack > 0:
# # #                     if s[idx] == '(':
# # #                         stack += 1
# # #                     elif s[idx] == ')':
# # #                         stack -= 1
# # #                     idx += 1
# # #                 if stack == 0:
# # #                     end_idx = idx
# # #                     expr = s[start_idx:idx-1]
# # #                     expressions.append((start_idx - 2, end_idx, expr))
# # #                 else:
# # #                     raise ValueError("Unmatched '(' in string")
# # #             else:
# # #                 idx += 1
# # #         return expressions

# # #     # Get the expressions and their positions
# # #     expressions = find_expressions(string)

# # #     # Initialize the result string
# # #     result = ''
# # #     last_idx = 0
# # #     for start, end, expr in expressions:
# # #         # Append the part of the string before the expression
# # #         result += string[last_idx:start]

# # #         # Prepare the local context for exec/eval
# # #         local_vars = {}
# # #         # Add existing variables to local_vars
# # #         for var_name, var_info in properties['default']['variables'].items():
# # #             local_vars[var_name] = var_info['value']

# # #         # Replace variables in expr
# # #         def replace_variables(expression):
# # #             # Match variables that are not preceded or followed by word characters
# # #             for var_name in properties['default']['variables']:
# # #                 var_pattern = r'(?<!\w)' + re.escape(var_name) + r'(?!\w)'
# # #                 var_value = var_name  # Keep the variable name as is
# # #                 expression = re.sub(var_pattern, var_value, expression)
# # #             return expression

# # #         expr_with_vars = replace_variables(expr)

# # #         # Determine if the expression is an assignment
# # #         is_assignment = '=' in expr_with_vars

# # #         # Execute the expression
# # #         try:
# # #             if is_assignment:
# # #                 exec(expr_with_vars, {}, local_vars)
# # #                 # Update properties with new or modified variables
# # #                 for var_name in local_vars:
# # #                     properties['default']['variables'][var_name] = {'value': local_vars[var_name], 'scope': 'local'}
# # #                 evaluated = ''  # Assignments don't produce output
# # #             else:
# # #                 evaluated = str(eval(expr_with_vars, {}, local_vars))
# # #         except Exception as e:
# # #             raise RuntimeError(f"Error evaluating expression '{expr_with_vars}': {e}")

# # #         # Append the evaluated result (or empty string) to the result
# # #         result += evaluated
# # #         last_idx = end

# # #     # Append any remaining part of the string
# # #     result += string[last_idx:]

# # #     return result


# if __name__ == "__main__":
#     # Example usage
#     properties = {
#         'default': {
#             'functions': {},
#             'variables': {
#                 'a': {'value': '10', 'scope': 'local'},   # String value
#                 'b': {'value': 1, 'scope': 'child'},      # Integer value
#                 't': {'value': 2, 'scope': 'parent'},     # Integer value
#                 'd': {'value': 4, 'scope': 'global'}      # Integer value
#             }
#         },
#         'controller': {
#             'functions': {},
#             'variables': {
#                 'a': {'value': '3', 'scope': 'local'},     # String value
#                 'b': {'value': 0, 'scope': 'child'},       # Integer value
#                 't': {'value': -1, 'scope': 'parent'},     # Integer value
#                 'd': {'value': -2, 'scope': 'global'},      # Integer value
#                 'w': {'value': dict(a=dict(a='10', b=dict(a='10', b=1, t=dict(a='10', b=1, t=2, d=4), d=4), t=2, d=4), b=1, t=2, d=4), 'scope': 'local'}
#             }
#         }
#     }



#     # Test case with an assignment
#     # string = "link_$(w=dict(a=dict(a='10', b=dict(a='10', b=1, t=dict(a='10', b=1, t=2, d=4), d=4), t=2, d=4), b=1, t=2, d=4))"
#     # result = process_value(string, properties)

#     # string = "link_$(pow(3, (int(w['a']['b']['t']['a'])+int(a))%3))"
#     string = "link_$(int(a))"
#     result = process_value(string, properties)
#     print(result)  # Expected output: 'link_'

#     # Verify that 'k' is now in properties
#     print("Updated properties:", properties['default']['variables'])

#     # Test case with an assignment

#     # string = "link_$(pow(3, (int(controller.w['a']['b']['t']['a'])+int(controller.a))%3))"
#     string = "link_$(int(controller.a))"
#     result = process_value(string, properties)
#     print(result)  # Expected output: 'link_'


# import re
# import flexidict

# def process_value(string, properties, local):
#     # Ensure that the input is processed only if it's a string
#     if not isinstance(string, str):
#         if isinstance(string, flexidict.FlexiDict):
#             string = flexidict.flexidict_to_dict(string)  # Convert FlexiDict to regular dict
#         if isinstance(string, list):
#             for i in range(len(string)):
#                 string[i] = process_value(string[i], properties, local)
#             return string  # Ensure to return the processed list here
#         elif isinstance(string, dict):
#             for key in list(string.keys()):
#                 string[key] = process_value(string[key], properties, local)
#             return string  # Return processed dictionary
#         elif isinstance(string, set):
#             string = {process_value(item, properties, local) for item in string}
#             return string  # Return processed set
#         else:
#             return string  # If it's another type, just return it

#     # Only process the expressions if it's a string
#     def find_expressions(s):
#         expressions = []
#         idx = 0
#         while idx < len(s):
#             if s[idx:idx + 2] == '$(':
#                 start_idx = idx + 2
#                 idx = start_idx
#                 stack = 1  # One '(' from '$('
#                 while idx < len(s) and stack > 0:
#                     if s[idx] == '(':
#                         stack += 1
#                     elif s[idx] == ')':
#                         stack -= 1
#                     idx += 1
#                 if stack == 0:
#                     end_idx = idx
#                     expr = s[start_idx:idx - 1]
#                     expressions.append((start_idx - 2, end_idx, expr))
#                 else:
#                     raise ValueError("Unmatched '(' in string")
#             else:
#                 idx += 1
#         return expressions

#     # Process the string if it's an actual string with expressions
#     expressions = find_expressions(string)
#     result = ''
#     last_idx = 0

#     for start, end, expr in expressions:
#         result += string[last_idx:start]

#         # Merge 'local' and 'properties' for evaluation
#         eval_context = {}
#         eval_context.update(local)  # Add local variables
#         eval_context.update({k: v['value'] for k, v in properties['default']['variables'].items()})  # Add properties variables

#         def replace_variables(expression):
#             tokens = expression.split('.')
            
#             # Check for namespace.variable (like controller.a)
#             if len(tokens) == 2 and tokens[0] in properties and tokens[1] in properties[tokens[0]]['variables']:
#                 return repr(properties[tokens[0]]['variables'][tokens[1]]['value'])

#             # Check default namespace and local for single variable name
#             if len(tokens) == 1:
#                 var_name = tokens[0]
#                 if var_name in properties['default']['variables']:
#                     return repr(properties['default']['variables'][var_name]['value'])
#                 if var_name in local:
#                     return repr(local[var_name])
            
#             return expression  # Return the expression unchanged if no match is found

#         # Replace variables in the expression
#         expr_with_vars = replace_variables(expr)

#         # Handle assignment: only allowed in local dictionary
#         is_assignment = '=' in expr_with_vars
#         if is_assignment:
#             var_name, var_value_expr = expr_with_vars.split('=', 1)
#             var_name = var_name.strip()

#             # Disallow assignment to properties, only assign to local
#             if var_name in properties['default']['variables'] or '.' in var_name:
#                 raise RuntimeError(f"Cannot assign to variable '{var_name}' in read-only context")
            
#             # Assign the value to the local dictionary
#             try:
#                 local[var_name] = eval(var_value_expr, {}, eval_context)
#                 evaluated = ''
#             except Exception as e:
#                 raise RuntimeError(f"Error evaluating assignment '{expr_with_vars}': {e}")
#         else:
#             try:
#                 evaluated = str(eval(expr_with_vars, {}, eval_context))
#             except Exception as e:
#                 raise RuntimeError(f"Error evaluating expression '{expr_with_vars}': {e}")

#         result += evaluated
#         last_idx = end

#     result += string[last_idx:]
#     return result


# if __name__ == '__main__':
#     # Example properties and local dictionaries
#     properties = {
#         'default': {
#             'variables': {
#                 'a': {'value': 10, 'scope': 'local'},
#                 'b': {'value': 20, 'scope': 'local'}
#             }
#         },
#         'controller': {
#             'variables': {
#                 'x': {'value': 100, 'scope': 'global'}
#             }
#         }
#     }

#     local = {
#         'c': 30
#     }

#     # Test cases with expressions
#     string = "link_$(a + b)"
#     result = process_value(string, properties, local)
#     print(result)  # Expected output: 'link_30'

#     string = "link_$(controller.x)"
#     result = process_value(string, properties, local)
#     print(result)  # Expected output: 'link_100'

#     string = "link_$(d = 40)$(d)"
#     result = process_value(string, properties, local)
#     print(result)  # Expected output: 'link_' and variable 'd' will be added to 'local'

#     print(local)  # Local now contains 'd': 40



import re
import flexidict
from pretty_print_dict import pretty_print_dict

# from ament_index_python.packages import get_package_share_directory


'''global variable for yamaro.py'''
current_properties = dict(default=dict(variables=dict(), functions=dict()))

current_local_key_list = []



def process(value) -> str:
    global current_properties, current_local_key_list
    # print(current_properties)
    # print()
    # print()
    # print()
    # print()
    return process_value(value, current_properties ,current_local_key_list)

def process_value(value, properties, local_key_list) -> str:
    # Ensure that the input is processed only if it's a string
    if not isinstance(value, str):
        if isinstance(value, flexidict.FlexiDict):
            value = flexidict.flexidict_to_dict(value)  # Convert FlexiDict to regular dict
        if isinstance(value, list):
            for i in range(len(value)):
                value[i] = process_value(value[i], properties, local_key_list)
            return value  # Ensure to return the processed list here
        elif isinstance(value, dict):
            for key in list(value.keys()):
                value[key] = process_value(value[key], properties, local_key_list)
            return value  # Return processed dictionary
        elif isinstance(value, set):
            value = {process_value(item, properties, local_key_list) for item in value}
            return value  # Return processed set
        else:
            return value  # If it's another type, just return it

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
    expressions = find_expressions(value)
    result = ''
    last_idx = 0

    for start, end, expr in expressions:
        result += value[last_idx:start]

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
                # for var_name in local_vars:
                #     # Track new local variables
                #     if var_name not in properties['default']['variables']:
                #         local_key_list.append(var_name)
                #         properties['default']['variables'][var_name] = {'value': local_vars[var_name], 'scope': 'local'}
                #     else:
                #         # Keep the existing scope of the variable
                #         current_scope = properties['default']['variables'][var_name]['scope']
                #         properties['default']['variables'][var_name] = {'value': local_vars[var_name], 'scope': current_scope}
                for var_name in local_vars:
                    # Strip extra quotes from the variable value
                    var_value = local_vars[var_name]
                    if isinstance(var_value, str):
                        var_value = var_value.strip('\'"')
                    # Track new local variables
                    if var_name not in properties['default']['variables']:
                        local_key_list.append(var_name)
                        properties['default']['variables'][var_name] = {'value': var_value, 'scope': 'local'}
                    else:
                        # Keep the existing scope of the variable
                        current_scope = properties['default']['variables'][var_name]['scope']
                        properties['default']['variables'][var_name] = {'value': var_value, 'scope': current_scope}

                evaluated = ''
            else:
                evaluated = str(eval(expr_with_vars, {}, local_vars))
        except Exception as e:
            raise RuntimeError(f"Error evaluating expression '{expr_with_vars}': {e}")

        result += evaluated
        last_idx = end

    result += value[last_idx:]
    return result


if __name__ == "__main__":
    current_properties = {
        'default': {
            'variables': {
                'x': {'value': 10, 'scope': 'global'}
            }
        },
        'namespace1': {
            'variables': {
                'y': {'value': 20, 'scope': 'local'}
            }
        }
    }
    current_local_key_list = []

    strin = 'root_link'
    processing_string = f'parent="{strin}"'
    print(process(f'$({processing_string})'))
    vari = 'parent'
    print(process(f'parent: $({vari})'))

    strin = 'root_link'
    processing_string = f' parent="{strin}"'
    print(process(f'$({processing_string})'))
    vari = 'parent'
    print(process(f'parent: $({vari})'))



    Q = 'a'
    print(process(f'$({vari})'))
    print(process(f"$({Q} = '1')"))
    print(process(f"$({Q})"))
    print(process(f"$({Q} = 2)"))
    print(process(f"$({Q})"))

    print(process(f"$((1, 1)[1])"))

    process(f"$(type = None)")

    print(current_properties)

    print(process(f'$(type)'))


    # # Example of setting global variables for testing
    # current_properties = {
    #     'default': {
    #         'variables': {
    #             'x': {'value': 10, 'scope': 'global'}
    #         }
    #     },
    #     'namespace1': {
    #         'variables': {
    #             'y': {'value': 20, 'scope': 'local'}
    #         }
    #     }
    # }
    # current_local_key_list = []

    # # Test value with embedded expressions
    # test_value = "Value of x is $(x) and y is $(namespace1.y)"
    
    # # Process the value
    # processed_result = process(test_value)
    
    # # Output the result
    # print(f"Processed result: {processed_result}")

    # print()
    # print()

    # print(current_local_key_list)

    # print()
    # print()

    # test2 = process("$(hi = 1)")

    # print(current_local_key_list)

    # print()
    # print()

    # current_local_key_list = []

    # test2 = process("$(x = 1)")

    # print(current_local_key_list)
    # print()
    # print()

    # print(pretty_print_dict(current_properties))
