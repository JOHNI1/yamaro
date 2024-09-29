import os
import sys
from flexidict import load_yaml_to_FlexiDict
from process_value import process
import process_value
from pretty_print_dict import pretty_print_dict
import copy

urdf_output = ''




def process_yaml_to_urdf(file_name, properties) -> dict:
    temp = process_value.current_properties
    process_value.current_properties = properties

    '''remove local parent variables and replace child scope with bridge scope'''
    for key in list(properties['default']['variables'].keys()):
        if properties['default']['variables'][key]['scope'] in 'local parent':
            del properties['default']['variables'][key]
        elif properties['default']['variables'][key]['scope'] in 'child':
            properties['default']['variables'][key]['scope'] = 'bridge'
    for key in list(properties['default']['functions'].keys()):
        if properties['default']['functions'][key]['scope'] in 'local parent':
            del properties['default']['functions'][key]
        elif properties['default']['functions'][key]['scope'] in 'child':
            properties['default']['functions'][key]['scope'] = 'bridge'

    top_local_key_list = []
    process_value.current_local_key_list = top_local_key_list
    file_data = load_yaml_to_FlexiDict(os.path.expanduser(file_name))
    # print(file_data)

    # Process variables and functions in the current file
    for key, value in file_data['variables'][-1]:
        tag = key.split('/')
        name = tag[0]
        scope = tag[1] if len(tag) == 2 else 'local'
        if scope not in 'local parent child global'.split():
            raise ValueError(f"The scope of variable '{name}' is wrong! 'local parent child global' are allowed")
        if name in properties['default']['variables'].keys() or (temp['default']['variables'][process(name)]['scope'] in 'child' and scope == 'parent') if temp is not None else False:
            raise ValueError(f"The variable '{name}' is already defined!")
        if '.' in key:
            raise ValueError(f"The variable '{name}' cannot contain dots.")
        properties['default']['variables'][process(name)] = {'value': process(value), 'scope': scope}

    for key, value in file_data['functions'][-1]:
        tag = key.split('/')
        name = tag[0]
        scope = tag[1] if len(tag) == 2 else 'local'
        if scope not in 'local parent child global'.split():
            raise ValueError(f"The scope of function '{name}' is wrong! 'local parent child global' are allowed")
        if name in properties['default']['functions'].keys() or (temp['default']['functions'][process(name)]['scope'] in 'child' and scope == 'parent') if temp is not None else False:
            raise ValueError(f"The function '{name}' is already defined!")
        if '.' in key:
            raise ValueError(f"The function '{name}' cannot contain dots.")
        if not name[0].isupper():
            raise ValueError(f"The function '{name}' must start with a capital letter!")
        properties['default']['functions'][process(name)] = {'value': value, 'scope': scope}



    print(properties)


    def process_level(layer: list, previous_level_local_key_list: list):
        local_key_list = []
        global current_local_key_list
        current_local_key_list = local_key_list

        for item in layer:
            if item[0] == 'part':
                try:
                    name = process(item[1]['name'][-1])
                    

                except Exception as e:
                    raise Exception(f"Error processing part. {e}")
             
            elif item[0] == 'process':
                pass
            elif item[0] == 'print':
                print(process(item[1]))
            elif item[0] == 'include':
                
                try:
                    namespace = process(item[1]['namespace'] if 'namespace' in item[1].keys() else 'default')
                    if not namespace[0].isupper() and namespace != 'default':
                        raise ValueError(f"The function '{item[1]['path']}' must start with a capital letter!")
                    a = process(item[1]['path'])
                    #the line beneath won't work when namespace is not default and not yet defined because **properties[namespace] is simply non existent and reading it will fail
                    #here I need to implement the logic of only merging values that are global, parent, bridge. ONLY THE VALUES, NOT THE SCOPE!
                    # properties[namespace] = {**properties[namespace], **process_yaml_to_urdf(a, copy.deepcopy(properties))['default']}
                    #if returned variable is bridge scope 
                    returned_properties = process_yaml_to_urdf(a, copy.deepcopy(properties))
                    for key in returned_properties['default']['variables'].keys():
                        if key in properties['default']['variables'].keys():
                            if properties['default']['variables'][key]['scope'] == 'local':
                                properties['default']['variables'][key] = returned_properties['default']['variables'][key]
                            else:
                                properties['default']['variables'][key]['value'] = returned_properties['default']['variables'][key]['value']
                        else:
                            properties['default']['variables'][key] = returned_properties['default']['variables'][key]

                    for key in returned_properties['default']['functions'].keys():
                        if key in properties['default']['functions'].keys():
                            if properties['default']['functions'][key]['scope'] == 'local':
                                properties['default']['functions'][key] = returned_properties['default']['functions'][key]
                            else:
                                properties['default']['functions'][key]['value'] = returned_properties['default']['functions'][key]['value']
                        else:
                            properties['default']['functions'][key] = returned_properties['default']['functions'][key]

                    process_value.current_properties = properties

                except Exception as e:
                    raise Exception(f"Error processing file '{item[1]['path']}'. {e}")


            elif item[0] == 'for':
                try:
                    iterator = process(item[1]['iterator'][0])
                    range_ = process(str(item[1]['range'][0]).split(','))

                    process(f'$({iterator} = 0)')

                    if len(range_) == 1:
                        range_.append(range_[0])
                        range_[0] = 0
                        range_.append(1)
                    else:
                        range_[2] = range_[2] if len(range_) == 3 else 1


                    for t in range(int(range_[0]), int(range_[1]), int(range_[2])):
                        process(f'$({iterator} = {t})')
                        
                        process_level(item[1]['body'][-1] if item[1]['body'][-1] is not None else [], local_key_list)########################## watch out! none type is not iterable error fix!
                except Exception as e:
                    raise Exception(f"Error processing for loop. {e}")

            elif item[0] == 'if':
                pass

            elif item[0][0].isupper():  #function
                tag = item[0].split('.')
                if len(tag) == 2 and tag[0] in properties.keys():
                    if tag[1] in properties[tag[0]]['functions'].keys():
                        pass

                    else:
                        raise KeyError(f"The function '{tag[1]}' is not defined in namespace '{tag[0]}'. Ensure that the function is defined in the same namespace or use default namespace.")

                elif len(tag) == 1 and tag in properties['default']['functions'].keys():
                    pass

                else:
                    raise ValueError(f"The '{tag}' is causing syntax error. For calling function, ensure that it is defined. If you specified namespace, use namespace.my_function to resolve it. Namespaces cannot be nested!")
            else:
                '''building of custom element and argument for super flexible xml tag creation!'''
                

        for key in local_key_list:
            if key in properties['default']['variables'].keys() and properties['default']['variables'][key]['scope'] == 'local':
                del properties['default']['variables'][key]
        process_value.current_local_key_list = previous_level_local_key_list




    process_level(file_data['model'][-1], top_local_key_list)


    for key in list(properties['default']['variables'].keys()):
        if properties['default']['variables'][key]['scope'] in 'local child':
            del properties['default']['variables'][key]
        elif properties['default']['variables'][key]['scope'] in 'parent':
            properties['default']['variables'][key]['scope'] = 'bridge'

    for key in list(properties['default']['functions'].keys()):
        if properties['default']['functions'][key]['scope'] in 'local child':
            del properties['default']['functions'][key]
        elif properties['default']['functions'][key]['scope'] in 'parent':
            properties['default']['functions'][key]['scope'] = 'bridge'

    '''properties should have only global, bridge and parent values'''
    return properties




    #AT THE END OF THE FUNCTION, 





    # print()
    # print()
    # print(file_data['model'])
    # print(file_data['model'][-1])

    # process_level(file_data['model'][-1])

    # # Process body if exists
    # body=None
    # try:
    #     body = file_data['body'][0]
    # except:
    #     pass
    
    # for component in body:
    #     if 'include' == component[0]:
    #         print(component)
    #         child_store = VariableStore()
    #         process_yaml_to_urdf(component[1]['path'][0], child_store, var_store, namespace=(component[1]['namespace'][0] if 'namespace' in component[1] else None))


    #     if 'process' in body:
    #         # Evaluate the process field using the variables
    #         local_vars = {**var_store.global_, **var_store.local}
    #         if parent_store:
    #             local_vars.update(parent_store.parent)
    #         local_vars.update(var_store.child)
    #         local_vars.update(var_store.parent)

    #         # Include all namespaces into the local vars for process execution
    #         local_vars.update(var_store.namespaces)
            
    #         eval(body['process'], {}, local_vars)

    # # After recursion, propagate variables back to the parent if needed
    # if parent_store:
    #     for var, value in var_store.parent.items():
    #         parent_store.set_variable(var, value, 'parent')
    #     for var, value in var_store.global_.items():
    #         parent_store.set_variable(var, value, 'global')

    # print(f"file_name: {file_name}, local, {get_variable}")





# Start with the first YAML file and a global variable store
properties = dict(default=dict(functions=dict(), variables=dict()))
print(properties)
print()
print()
print()
print()



# process input arg so it allows passing variables! for now I will pass barebone properties

process_yaml_to_urdf(sys.argv[1], properties)

print(urdf_output)
