import os
import sys
from flexidict import load_yaml_to_FlexiDict
from process_value import process
import process_value
from pretty_print_dict import pretty_print_dict
import copy
import re

urdf_output = '<?xml version="1.0" ?>\n'
spaces = 0
tab = 2

def tab_():
    global spaces
    spaces += tab

def untab_():
    global spaces
    spaces -= tab

def add_line_to_urdf(line):
    global urdf_output
    urdf_output += f"{' ' * spaces}{line}\n"

def split_(s):
    # Split on any number of commas and spaces
    return re.split(r'[,\s]+', s.strip())


def xml(element, attributes={}, body=[], *args, **kwargs):
    if len(body) > 0:
        argument = ''.join(f' {key}="{attributes[key]}"' for key in attributes.keys())
        add_line_to_urdf(f'<{element}{argument}>')
        tab_()
    
        for func in body:
            func(*args, **kwargs)

        untab_()
        add_line_to_urdf(f'</{element}>')
    else:
        argument = ''.join(f' {key}="{attributes[key]}"' for key in attributes.keys())
        add_line_to_urdf(f'<{element}{argument}/>')
        

def part_process(item, previous_level_local_key_list, process_level, *args, **kwargs):
    # def get_value(item_, key, default) -> any:
    #     if key in item_.keys() :
    #         k = process(key)
    #         if item_[k][-1] is not None:
    #             del item_[k]
    #             return process(item_[key][-1])
    #         del item_[k]
    #     return default
    def get_value(item_, default) -> any:
        if item_[1] is None:
            return default
        return process(item_[1])
    
    try:
        if process(item[0][0]) == 'name':
            name = split_(process(item[0][1]))
            if len(name) == 1:
                name.append(f'{name[0]}_link')
                name[0] = f'{name[0]}_joint'
        else:
            raise ValueError(f'In part, first define name, then joint and then link!')

        if process(item[1][0]) == 'joint':
            joint = item[1][1]
        else:
            raise ValueError(f'In part, first define name, then joint and then link!')

        vars = dict(type='type', parent=None, xyz='0 0 0', rpy='0 0 0')

        j = []

        for item_ in joint:
            key = process(item_[0])
            if key in vars.keys():
                vars[key] = process(item_[1])
            else:
                key = key.split('/')
                attributes = key[1].split(',')
                att = {}
                for attribute in attributes:
                    att[attribute.split(':=')[0]] = attribute.split('=')[1]
                j.append(lambda: xml(key[0], att, process_level(item_[1], previous_level_local_key_list))) #no processing here!


        origin = {'xyz': vars['xyz'], 'rpy': vars['rpy']}
        child = {'link': name[1]}
        parent = {'link': vars['parent']}

        default_joint_setup = [
            lambda: xml('origin', origin),
            lambda: xml('child', child),
            lambda: xml('parent', parent),
        ]

        for i in default_joint_setup:
            j.insert(default_joint_setup[i], i)

        xml('joint', {'name': name[0], 'type': type}, j)





        if not process(item[2][0]) == 'link':
            link = item[2][1]
        else:
            raise ValueError(f'In part first define name, then joint and then link!')

        vars = dict(geometry=None, scale=None, mass=None, xyz='0 0 0', rpy='0 0 0')

        l = []

        for item_ in link:
            key = process(item_[0])
            if key in vars.keys():
                vars[key] = process(item_[1])
            elif key in 'visual inertial collision'.split():
                sub_vars = copy.deepcopy(vars)
                l_comp = []
                if sub_key == 'inertial':
                    for sub_item in item_[1]:
                        sub_key = process(sub_item[0])
                        if sub_key in 'xyz rpy'.split():
                            sub_vars[sub_key] = ''.join(str(float(split_(sub_vars[sub_key])[i]) + float(split_(process(sub_item[1]))[i])) for i in range(3))         
                        elif sub_key in 'inertia geometry'.split():
                            sub_vars[sub_key] = process(sub_item[1])

                            l_comp.append(lambda: xml(key, {}))
                        elif sub_key in 'mass'.split():
                            sub_vars[sub_key] = process(sub_item[1])
                        else:
                            l_comp.append(lambda: xml(key, {}))



                    if 'inertia' not in sub_vars.keys():
                        if sub_vars['geometry'].lower() == 'box':
                            sub_vars['inertia'] = f'{float(sub_vars['mass']) * (pow(float(split_(sub_vars['scale'])[1]),2) + pow(float(split_(sub_vars['scale'])[2]),2)) / 12} 0 0 {float(sub_vars['mass']) * (pow(float(split_(sub_vars['scale'])[0]),2) + pow(float(split_(sub_vars['scale'])[2]),2)) / 12} 0 {float(sub_vars['mass']) * (pow(float(split_(sub_vars['scale'])[0]),2)+ pow(float(split_(sub_vars['scale'])[1]),2)) / 12}'
                        elif sub_vars['geometry'].lower() == 'cylinder':
                            sub_vars['inertia'] = f'{float(sub_vars['mass']) * (3*pow(float(split_(sub_vars['scale'])[0]),2) + pow(float(split_(sub_vars['scale'])[1]),2)) / 12} 0 0 {float(sub_vars['mass']) * (3*pow(float(split_(sub_vars['scale'])[0]),2) + pow(float(split_(sub_vars['scale'])[1]),2)) / 12} 0 {float(sub_vars['mass']) * pow(float(split_(sub_vars['scale'])[0]),2) / 2}'
                        elif sub_vars['geometry'].lower() == 'tube': # first two is inner or outer diameter and last is length... inner and outer dimater order dooes not matter...
                            sub_vars['inertia'] = f'{float(sub_vars['mass']) * (3*(pow(float(split_(sub_vars['scale'])[0]),2) + pow(float(split_(sub_vars['scale'])[1]),2)) + pow(float(split_(sub_vars['scale'])[2]),2)) / 12} 0 0 {float(sub_vars['mass']) * (3*(pow(float(split_(sub_vars['scale'])[0]),2) + pow(float(split_(sub_vars['scale'])[1]),2)) + pow(float(split_(sub_vars['scale'])[2]),2)) / 12} 0 {float(sub_vars['mass']) * (pow(float(split_(sub_vars['scale'])[0]),2) + pow(float(split_(sub_vars['scale'])[1]),2)) / 2}'
                        elif sub_vars['geometry'].lower() == 'sphere':
                            sub_vars['inertia'] = f'{float(sub_vars['mass']) * pow(float(split_(sub_vars['scale'])[0]),2) * (2/5)} 0 0 {float(sub_vars['mass']) * pow(float(split_(sub_vars['scale'])[0]),2) * (2/5)} 0 {float(sub_vars['mass']) * pow(float(split_(sub_vars['scale'])[0]),2) * (2/5)}'

                            
                        
                    
                    l_comp.append(lambda: xml('mass', attributes=dict(value=sub_vars['mass'])))
                    l_comp.append(lambda: xml('inertia', attributes=dict(xyz=(sub_vars['xyz']), rpy=(sub_vars['inertia']))))
                    l_comp.append(lambda: xml('origin', attributes=dict(ixx=(split_(sub_vars['inertia']))[0], ixy=(split_(sub_vars['inertia']))[1], ixz=(split_(sub_vars['inertia']))[2], iyy=(split_(sub_vars['inertia']))[3], iyz=(split_(sub_vars['inertia']))[4], izz=(split_(sub_vars['inertia']))[5])))

                        


                if sub_key in 'collision visual'.split():
                #     for sub_item in item_[1]:
                #         sub_key = process(sub_item[0])


                # l.append(lambda: xml(key, body=l_comp))
                    for sub_item in item_[1]:
                        sub_key = process(sub_item[0])
                        if sub_key in 'xyz rpy'.split():
                            sub_vars[sub_key] = ''.join(str(float(split_(sub_vars[sub_key])[i]) + float(split_(process(sub_item[1]))[i])) for i in range(3))         
                        elif sub_key in 'inertia geometry'.split():
                            sub_vars[sub_key] = process(sub_item[1])

                            l_comp.append(lambda: xml(key, {}))
                        elif sub_key in 'mass'.split():
                            sub_vars[sub_key] = process(sub_item[1])



                    if 'inertia' not in sub_vars.keys():
                        if sub_vars['geometry'].lower() == 'box':
                            sub_vars['inertia'] = f'{float(sub_vars['mass']) * (pow(float(split_(sub_vars['scale'])[1]),2) + pow(float(split_(sub_vars['scale'])[2]),2)) / 12} 0 0 {float(sub_vars['mass']) * (pow(float(split_(sub_vars['scale'])[0]),2) + pow(float(split_(sub_vars['scale'])[2]),2)) / 12} 0 {float(sub_vars['mass']) * (pow(float(split_(sub_vars['scale'])[0]),2)+ pow(float(split_(sub_vars['scale'])[1]),2)) / 12}'
                        elif sub_vars['geometry'].lower() == 'cylinder':
                            sub_vars['inertia'] = f'{float(sub_vars['mass']) * (3*pow(float(split_(sub_vars['scale'])[0]),2) + pow(float(split_(sub_vars['scale'])[1]),2)) / 12} 0 0 {float(sub_vars['mass']) * (3*pow(float(split_(sub_vars['scale'])[0]),2) + pow(float(split_(sub_vars['scale'])[1]),2)) / 12} 0 {float(sub_vars['mass']) * pow(float(split_(sub_vars['scale'])[0]),2) / 2}'
                        elif sub_vars['geometry'].lower() == 'tube': # first two is inner or outer diameter and last is length... inner and outer dimater order dooes not matter...
                            sub_vars['inertia'] = f'{float(sub_vars['mass']) * (3*(pow(float(split_(sub_vars['scale'])[0]),2) + pow(float(split_(sub_vars['scale'])[1]),2)) + pow(float(split_(sub_vars['scale'])[2]),2)) / 12} 0 0 {float(sub_vars['mass']) * (3*(pow(float(split_(sub_vars['scale'])[0]),2) + pow(float(split_(sub_vars['scale'])[1]),2)) + pow(float(split_(sub_vars['scale'])[2]),2)) / 12} 0 {float(sub_vars['mass']) * (pow(float(split_(sub_vars['scale'])[0]),2) + pow(float(split_(sub_vars['scale'])[1]),2)) / 2}'
                        elif sub_vars['geometry'].lower() == 'sphere':
                            sub_vars['inertia'] = f'{float(sub_vars['mass']) * pow(float(split_(sub_vars['scale'])[0]),2) * (2/5)} 0 0 {float(sub_vars['mass']) * pow(float(split_(sub_vars['scale'])[0]),2) * (2/5)} 0 {float(sub_vars['mass']) * pow(float(split_(sub_vars['scale'])[0]),2) * (2/5)}'

                            
                        
                    
                    l_comp.append(lambda: xml('mass', attributes=dict(value=sub_vars['mass'])))
                    l_comp.append(lambda: xml('inertia', attributes=dict(xyz=(sub_vars['xyz']), rpy=(sub_vars['inertia']))))
                    l_comp.append(lambda: xml('origin', attributes=dict(ixx=(split_(sub_vars['inertia']))[0], ixy=(split_(sub_vars['inertia']))[1], ixz=(split_(sub_vars['inertia']))[2], iyy=(split_(sub_vars['inertia']))[3], iyz=(split_(sub_vars['inertia']))[4], izz=(split_(sub_vars['inertia']))[5])))

                        


            else:
                l.append(lambda: xml(key[0], att, process_level(item_[1], previous_level_local_key_list))) #no processing here!



        # for item_ in link:
        #     key = process(item_[0])
        #     if :
                

        #     elif key in 'inertial collision visual'.split():
        #         xyz = ''.join(str(float(split_(get_value(item_[1], 'xyz', '0 0 0'))[i]) + float(split_(xyz)[i])) for i in range(3))                
        #         rpy = get_value(item_[1], 'rpy', '0 0 0')

        #         if key == 'inertial':
        #             l.append(lambda: xml('inertial', body=[

        #             ]))
        #         elif key == 'collision':
        #             l.append(lambda: xml('collision', body=[
        #                 lambda: xml('geometry', body=[
        #                     lambda: xml('inertial', body=[])
        #                 ])
        #             ]))
        #         elif key == 'visual':
        #             l.append(lambda: xml('visual', body=[ 
        #             ]))
        #     else:


                

        # xml('link', {'name': name[1]},
        #     [
        #     lambda: xml('origin', origin),
        #     lambda: xml('child', child),
        #     lambda: xml('parent', parent),
        #     ]
        # )
 

    except Exception as e:
        raise Exception(f"Error processing part. {e}")


def process_yaml_to_urdf(file_name, properties, yaml_path_list) -> dict:
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

    print('before: ',properties, '\n')

    # Process variables and functions in the current file
    for key, value in file_data['variables'][-1] if file_data['variables'][-1] is not None else []:
        tag = key.split('/')
        name = process(tag[0])
        scope = process(tag[1] if len(tag) == 2 else 'local')
        if scope not in 'local parent child global'.split():
            raise ValueError(f"The scope of variable '{name}' is wrong! 'local parent child global' are allowed")
        if name in properties['default']['variables'].keys():
            if properties['default']['variables'][name]['scope'] != 'arg':
                raise ValueError(f"The variable '{name}' is already defined!")
        if (temp['default']['variables'][name]['scope'] in 'child parent' and scope in 'parent global') if name in temp['default']['variables'].keys() else False:
            raise ValueError(f"The variable '{name}' is already defined!")
        if '.' in key:
            raise ValueError(f"The variable '{name}' cannot contain dots.")
        if name in properties['default']['variables'].keys():
            if properties['default']['variables'][name]['scope'] != 'arg':
                properties['default']['variables'][name] = {'value': process(value), 'scope': scope}
        else:
            properties['default']['variables'][name] = {'value': process(value), 'scope': scope}

    for key, value in file_data['functions'][-1] if file_data['functions'][-1] is not None else []:
        tag = key.split('/')
        name = process(tag[0])
        scope = process(tag[1] if len(tag) == 2 else 'local')
        if scope not in 'local parent child global'.split():
            raise ValueError(f"The scope of function '{name}' is wrong! 'local parent child global' are allowed")
        if name in properties['default']['functions'].keys():
            raise ValueError(f"The function '{name}' is already defined!")
        if (temp['default']['functions'][name]['scope'] in 'child parent' and scope in 'parent global') if name in temp['default']['functions'].keys() else False:
            raise ValueError(f"The function '{name}' is already defined!")
        if '.' in key:
            raise ValueError(f"The function '{name}' cannot contain dots.")
        if not name[0].isupper():
            raise ValueError(f"The function '{name}' must start with a capital letter!")
        properties['default']['functions'][process(name)] = {'value': value, 'scope': scope}









    def process_level(layer: list, previous_level_local_key_list: list):
        local_key_list = []
        global current_local_key_list
        current_local_key_list = local_key_list

        for item in layer if layer is not None else []:
            item[0] = process(item[0])################## still not sure if its good idea to change the original yaml read data
            # print(file_data)

            if item[0] == 'part':
                part_process(copy.deepcopy(item[1]))

            elif item[0] == 'process':
                pass
            elif item[0] == 'print':
                # ANSI escape codes for colors
                GREEN = "\033[32m"
                RESET = "\033[0m"  # Reset color to default
                print(f'{GREEN}user_print:{RESET} {process(item[1])}')
            elif item[0] == 'include':
                
                try:
                    namespace = process(item[1]['namespace'][-1] if 'namespace' in item[1].keys() else 'default')
                    if not namespace[0].isupper() and namespace != 'default':
                        raise ValueError(f"The function '{item[1]['path']}' must start with a capital letter!")
                    path = process(item[1]['path'][-1])
                    if path in yaml_path_list:
                        raise Exception("path included is already used and it will cuase infinite recursion!")
                    #the line beneath won't work when namespace is not default and not yet defined because **properties[namespace] is simply non existent and reading it will fail
                    #here I need to implement the logic of only merging values that are global, parent, bridge. ONLY THE VALUES, NOT THE SCOPE!
                    # properties[namespace] = {**properties[namespace], **process_yaml_to_urdf(a, copy.deepcopy(properties))['default']}
                    #if returned variable is bridge scope 
                    returned_properties = process_yaml_to_urdf(path, copy.deepcopy(properties), (copy.deepcopy(yaml_path_list)).append(path))
                    if namespace not in properties:
                        properties[namespace] = dict(variables = dict(), functions = dict())
                    for key in returned_properties['default']['variables'].keys():
                        if key in properties[namespace]['variables'].keys():
                            if properties[namespace]['variables'][key]['scope'] == 'local':
                                properties[namespace]['variables'][key] = returned_properties['default']['variables'][key]
                            else:
                                properties[namespace]['variables'][key]['value'] = returned_properties['default']['variables'][key]['value']
                        else:
                            properties[namespace]['variables'][key] = returned_properties['default']['variables'][key]

                    for key in returned_properties['default']['functions'].keys():
                        if key in properties[namespace]['functions'].keys():
                            if properties[namespace]['functions'][key]['scope'] == 'local':
                                properties[namespace]['functions'][key] = returned_properties['default']['functions'][key]
                            else:
                                properties[namespace]['functions'][key]['value'] = returned_properties['default']['functions'][key]['value']
                        else:
                            properties[namespace]['functions'][key] = returned_properties['default']['functions'][key]


                    process_value.current_properties = properties

                except Exception as e:
                    raise Exception(f"Error processing file '{item[1]['path']}'. {e}")


            elif item[0] == 'for':
                try:
                    iterator = process(item[1]['iterator'][0])
                    range_ = split_(process(str(item[1]['range'][0])))

                    process(f'$({iterator} = 0)')

                    if len(range_) == 1:
                        range_.append(range_[0])
                        range_[0] = 0
                        range_.append(1)
                    elif len(range_) == 2:
                        range_.append(1)

                    for t in range(int(range_[0]), int(range_[1]), int(range_[2])):
                        process(f'$({iterator} = {t})')
                        
                        process_level(item[1]['body'][-1], local_key_list)########################## watch out! none type is not iterable error fix!
                except Exception as e:
                    raise Exception(f"Error processing for loop. {e}")

            elif item[0] == 'if':
                try:
                    condition = process(item[1]['condition'][0])
                    if (eval(condition)):
                        process_level(item[1]['body'][-1], local_key_list)########################## watch out! none type is not iterable error fix!
                except Exception as e:
                    raise Exception(f"Error processing for loop. {e}")
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
    print('after: ',properties, '\n')


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





# ANSI escape codes for colors
RED = "\033[31m"
GREEN = "\033[32m"
YELLOW = "\033[33m"
BLUE = "\033[34m"
RESET = "\033[0m"  # Reset color to default

# # Example of printing in different colors
# print(f"{RED}This is red text{RESET}")
# print(f"{GREEN}This is green text{RESET}")
# print(f"{YELLOW}This is yellow text{RESET}")
# print(f"{BLUE}This is blue text{RESET}")

# Start with the first YAML file and a global variable store
properties = dict(default=dict(variables=dict(), functions=dict()))

for idx, arg in enumerate(sys.argv):
    print(f"Argument {idx}: {arg}")
    if idx > 1:
        name, value = arg.split(':=')
        process(f'$({name} = {value})')
        properties['default']['variables'][name] = {'value': eval(value), 'scope': 'arg'}
        print(properties)



if 'robot' in load_yaml_to_FlexiDict(os.path.expanduser(sys.argv[1])).keys():
    add_line_to_urdf(f'<robot name="{process(load_yaml_to_FlexiDict(os.path.expanduser(sys.argv[1]))['robot'][0])}">')
else:
    add_line_to_urdf(f'<robot name="default">')
tab_()
add_line_to_urdf('')
add_line_to_urdf(f'<link name="root_link">')
add_line_to_urdf(f'</link>\n')


# print(load_yaml_to_FlexiDict(os.path.expanduser(sys.argv[1])))

process_value.current_properties = properties
print(f'\n{BLUE}starting processing yaml to urdf!{RESET}\n')

# process input arg so it allows passing variables! for now I will pass barebone properties
process_yaml_to_urdf(sys.argv[1], properties, [sys.argv[1]])
untab_()
add_line_to_urdf('</robot>')


print(f'\n\n{BLUE}output urdf:{RESET}\n{urdf_output}')
