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

import os
import sys
import copy
import re
import numpy as np
from .flexidict import load_yaml_to_FlexiDict, FlexiDict
from .process_value import process
from . import process_value
# from .pretty_print_dict import pretty_print_dict

urdf_output = '<?xml version="1.0" ?>\n'
spaces = 0
TAB = 2




def tab_():
    global spaces
    spaces += TAB

def untab_():
    global spaces
    spaces -= TAB

def add_line_to_urdf(line):

    global urdf_output
    urdf_output += f"{' ' * spaces}{line}\n"

def split_(s):
    # Split on any number of commas and spaces
    return re.split(r'[,\s]+', s.strip())


def xml(element, attributes={}, body=[], *args, **kwargs):
    if len(body) > 0:
        argument = ''.join(' {key}="{value}"'.format(key=key, value=str(attributes[key]).strip('\'"')) for key in attributes)
        add_line_to_urdf('<{element}{argument}>'.format(element=element, argument=argument))
        tab_()
    
        for func in body:
            func(*args, **kwargs)

        untab_()
        add_line_to_urdf('</{element}>'.format(element=element))
    else:
        argument = ''.join(' {key}="{value}"'.format(key=key, value=str(attributes[key]).strip('\'"')) for key in attributes)
        add_line_to_urdf('<{element}{argument}/>'.format(element=element, argument=argument))
        

def rotate_vector(vector, rotation_vector):

    if ([(float(vector[i])) for i in range(3)] if isinstance(vector[0], str) else vector) == [0, 0, 0]:
        return [0, 0, 0]
    # Create rotation matrices for roll, pitch, and yaw
    Rx = np.array([
        [1, 0, 0],
        [0, np.cos(float(rotation_vector[0])), -np.sin(float(rotation_vector[0]))],
        [0, np.sin(float(rotation_vector[0])), np.cos(float(rotation_vector[0]))]
    ])
    
    Ry = np.array([
        [np.cos(float(rotation_vector[1])), 0, np.sin(float(rotation_vector[1]))],
        [0, 1, 0],
        [-np.sin(float(rotation_vector[1])), 0, np.cos(float(rotation_vector[1]))]
    ])
    
    Rz = np.array([
        [np.cos(float(rotation_vector[2])), -np.sin(float(rotation_vector[2])), 0],
        [np.sin(float(rotation_vector[2])), np.cos(float(rotation_vector[2])), 0],
        [0, 0, 1]
    ])
    
    # Combined rotation matrix
    R = Rz @ Ry @ Rx
    
    # Rotate the vector
    rotated_vector = R @ np.array([float(value) for value in vector])
    
    return rotated_vector

def part_process(item, local_key_list, process_level):

    try:
        my_item = copy.deepcopy(item)
        # for ind in range(len(my_item.keys())):
        #     my_item[ind][0] = process(my_item[ind][0])
        
        if ['name', 'joint', 'link'] != [ele for ele in my_item.keys() if ele in ['name', 'joint', 'link']]:
            raise ValueError(f'In part, define name, then joint and then link!')
        part_extras = FlexiDict()
        for the_index, the_key in enumerate(my_item.keys()):
            
            if the_key == 'name':
                name = split_(process(my_item[the_index][1]))
                if len(name) == 1:
                    name.append(f'{name[0]}_link')
                    name[0] = f'{name[0]}_joint'
                    
            elif the_key == 'joint':
                joint = my_item[the_index][1]
                    
                vars = dict(type='type', parent=None, xyz='0 0 0', rpy='0 0 0', pivot='0 0 0')

                j = []

                j_extras = FlexiDict()

                for item_ in joint:
                    key = process(item_[0])
                    # if key in vars.keys():
                    #     value = process(item_[1])
                    #     vars[key] = value if value is not None else vars[key]
                    if key in list(vars.keys()):
                        value = process(item_[1])
                        if isinstance(value, str):
                            value = value.strip('\'"')
                        vars[key] = value if value is not None else vars[key]
                    else:
                        j_extras.add(key, item_[1])
                        
                final_xyz = rotate_vector(split_(vars['pivot']), split_(vars['rpy']))
                vars['xyz'] = ' '.join(str(float(split_(vars['xyz'])[i]) - final_xyz[i]) for i in range(3))
                origin = {
                    'xyz': vars['xyz'],
                    'rpy': vars['rpy']
                }
                child = {'link': name[1]}
                parent = {'link': vars['parent']}

                default_joint_setup = [
                    lambda origin=origin: xml('origin', origin),
                    lambda child=child: xml('child', child),
                    lambda parent=parent: xml('parent', parent),
                ]

                for i in range(len(default_joint_setup)):
                    j.insert(i, default_joint_setup[i])

                j.append(lambda j_extras=j_extras: process_level(j_extras, local_key_list))

                xml('joint', {'name': name[0], 'type': vars['type']}, j)






            elif my_item[the_index][0] == 'link':
                link = my_item[the_index][1]
                    
                vars = dict(geometry=None, scale=None, mass=None, xyz='0 0 0', rpy='0 0 0', pivot='0 0 0')

                l = []
                l_extras = FlexiDict()
                l_comp_list = []
                
                for index, item_ in enumerate(link):
                    key = process(item_[0])
                    l_comp_extras = FlexiDict()

                    l_comp_list.append([])


                    if key in vars.keys():
                        value = process(item_[1])
                        if isinstance(value, str):
                            value = value.strip('\'"')
                        vars[key] = value if value is not None else vars[key]

                    elif key in 'visual inertial collision'.split():
                        sub_vars = copy.deepcopy(vars)
                        sub_vars['xyz'] = '0 0 0'
                        sub_vars['pivot'] = '0 0 0' #reset pivot
                        sub_vars['rpy'] = '0 0 0'
                        if key == 'inertial':
                            for sub_item in item_[1] if item_[1] is not None else [['']]:
                                sub_key = process(sub_item[0])
                                if sub_key in sub_vars.keys() and not sub_key == '':
                                    sub_value = process(sub_item[1])
                                    sub_vars[sub_key] = sub_value if sub_value is not None else sub_vars[sub_key]
                                elif not sub_key == '':
                                    l_comp_extras.add(sub_key, sub_item[1])
                                    

                            if 'inertia' not in sub_vars.keys():
                                if sub_vars['geometry'].lower() == 'box':
                                    sub_vars['inertia'] = f"{float(sub_vars['mass']) * (pow(float(split_(sub_vars['scale'])[1]), 2) + pow(float(split_(sub_vars['scale'])[2]), 2)) / 12} 0 0 {float(sub_vars['mass']) * (pow(float(split_(sub_vars['scale'])[0]), 2) + pow(float(split_(sub_vars['scale'])[2]), 2)) / 12} 0 {float(sub_vars['mass']) * (pow(float(split_(sub_vars['scale'])[0]), 2) + pow(float(split_(sub_vars['scale'])[1]), 2)) / 12}"
                                elif sub_vars['geometry'].lower() == 'cylinder':
                                    sub_vars['inertia'] = f"{float(sub_vars['mass']) * (3 * pow(float(split_(sub_vars['scale'])[0]), 2) + pow(float(split_(sub_vars['scale'])[1]), 2)) / 12} 0 0 {float(sub_vars['mass']) * (3 * pow(float(split_(sub_vars['scale'])[0]), 2) + pow(float(split_(sub_vars['scale'])[1]), 2)) / 12} 0 {float(sub_vars['mass']) * pow(float(split_(sub_vars['scale'])[0]), 2) / 2}"
                                elif sub_vars['geometry'].lower() == 'tube':
                                    sub_vars['inertia'] = f"{float(sub_vars['mass']) * (3 * (pow(float(split_(sub_vars['scale'])[0]), 2) + pow(float(split_(sub_vars['scale'])[1]), 2)) + pow(float(split_(sub_vars['scale'])[2]), 2)) / 12} 0 0 {float(sub_vars['mass']) * (3 * (pow(float(split_(sub_vars['scale'])[0]), 2) + pow(float(split_(sub_vars['scale'])[1]), 2)) + pow(float(split_(sub_vars['scale'])[2]), 2)) / 12} 0 {float(sub_vars['mass']) * (pow(float(split_(sub_vars['scale'])[0]), 2) + pow(float(split_(sub_vars['scale'])[1]), 2)) / 2}"
                                elif sub_vars['geometry'].lower() == 'sphere':
                                    sub_vars['inertia'] = f"{float(sub_vars['mass']) * pow(float(split_(sub_vars['scale'])[0]), 2) * (2 / 5)} 0 0 {float(sub_vars['mass']) * pow(float(split_(sub_vars['scale'])[0]), 2) * (2 / 5)} 0 {float(sub_vars['mass']) * pow(float(split_(sub_vars['scale'])[0]), 2) * (2 / 5)}"

                            l_comp_list[index].append(lambda sub_vars=sub_vars: xml('mass', attributes=dict(value=sub_vars['mass'])))


                            transformed_xyz = rotate_vector(split_(vars['pivot']), split_(vars['rpy']))
                            sub_sub_transformed_xyz = rotate_vector(split_(sub_vars['pivot']), split_(sub_vars['rpy']))
                            sub_transformed_xyz = rotate_vector([(float(split_(sub_vars['xyz'])[i]) - sub_sub_transformed_xyz[i]) for i in range(3)], split_(vars['rpy']))

                            sub_vars['xyz'] = ' '.join(str(float(split_(vars['xyz'])[i]) - transformed_xyz[i] + sub_transformed_xyz[i]) for i in range(3))
                            sub_vars['rpy'] = ' '.join(str(float(split_(sub_vars['rpy'])[i]) + float(split_(vars['rpy'])[i])) for i in range(3))
                            l_comp_list[index].append(lambda sub_vars=sub_vars: xml('origin', attributes=dict(xyz=sub_vars['xyz'], rpy=sub_vars['rpy'])))
                            inertia_values = split_(sub_vars['inertia'])
                            l_comp_list[index].append(
                                lambda inertia_values=inertia_values: xml(
                                    'inertia',
                                    attributes=dict(
                                        ixx=inertia_values[0],
                                        ixy=inertia_values[1],
                                        ixz=inertia_values[2],
                                        iyy=inertia_values[3],
                                        iyz=inertia_values[4],
                                        izz=inertia_values[5],
                                    ),
                                )
                            )
                            l_comp_list[index].append(lambda l_comp_extras=l_comp_extras: process_level(l_comp_extras, local_key_list))
                            l.append(lambda key=key, body=l_comp_list[index]: xml(key, body=body))

                        elif key in 'collision visual'.split():
                            for sub_item in item_[1] if item_[1] is not None else [['']]:
                                sub_key = process(sub_item[0])
                                if sub_key in sub_vars.keys() and not sub_key == '':
                                    sub_value = process(sub_item[1])
                                    sub_vars[sub_key] = sub_value if sub_value is not None else sub_vars[sub_key]
                                elif not sub_key == '':
                                    l_comp_extras.add(sub_key, sub_item[1])
                                    
                            match sub_vars['geometry'].lower(): 
                                case 'box':
                                    l_comp_list[index].append(
                                        lambda sub_vars=sub_vars: xml('geometry', body=[lambda sub_vars=sub_vars: xml('box', attributes=dict(size=sub_vars['scale']))])
                                    )
                                case 'cylinder':
                                    radius, length = float(split_(sub_vars['scale'])[0]), float(split_(sub_vars['scale'])[1])
                                    l_comp_list[index].append(
                                        lambda radius=radius, length=length: xml(
                                            'geometry', body=[lambda: xml('cylinder', attributes=dict(radius=radius, length=length))]
                                        )
                                    )
                                case 'sphere':
                                    radius = float(split_(sub_vars['scale'])[0])
                                    l_comp_list[index].append(
                                        lambda radius=radius: xml('geometry', body=[lambda: xml('sphere', attributes=dict(radius=radius))])
                                    )
                                case _:
                                    l_comp_list[index].append(
                                        lambda sub_vars=sub_vars: xml('geometry', body=[lambda sub_vars=sub_vars: xml('mesh', attributes=dict(filename=sub_vars['geometry'], scale=sub_vars['scale']))])
                                    )



                            transformed_xyz = rotate_vector(split_(vars['pivot']), split_(vars['rpy']))
                            sub_sub_transformed_xyz = rotate_vector(split_(sub_vars['pivot']), split_(sub_vars['rpy']))
                            sub_transformed_xyz = rotate_vector([(float(split_(sub_vars['xyz'])[i]) - sub_sub_transformed_xyz[i]) for i in range(3)], split_(vars['rpy']))

                            sub_vars['xyz'] = ' '.join(str(float(split_(vars['xyz'])[i]) - transformed_xyz[i] + sub_transformed_xyz[i]) for i in range(3))
                            sub_vars['rpy'] = ' '.join(str(float(split_(sub_vars['rpy'])[i]) + float(split_(vars['rpy'])[i])) for i in range(3))

                            l_comp_list[index].append(
                                lambda sub_vars=sub_vars: xml('origin', attributes=dict(xyz=sub_vars['xyz'], rpy=sub_vars['rpy']))
                            )

                            l_comp_list[index].append(lambda l_comp_extras=l_comp_extras: process_level(l_comp_extras, local_key_list))
                            l.append(lambda key=key, body=l_comp_list[index]: xml(key, body=body))
                    else:
                        l_extras.add(key, item_[1])
        
                l.append(lambda l_extras=l_extras: process_level(l_extras, local_key_list))
                xml('link', {'name': name[1]}, l)

            else:
                part_extras.add(the_key, my_item[the_index][1])
            
        process_level(part_extras, local_key_list)
            



    except Exception as e:
        raise Exception(f"Error processing part. {e}")


ite = 0
def process_yaml_to_urdf(file_name, properties, yaml_path_list) -> dict:
    # temp = process_value.current_properties
    process_value.current_properties = properties

    '''remove local, parent variables and replace child scope with bridge scope'''
    for ns_ in properties.keys():
        for key in list(properties[ns_]['variables'].keys()):
            if properties[ns_]['variables'][key]['scope'] in 'local parent':
                del properties[ns_]['variables'][key]
            elif properties[ns_]['variables'][key]['scope'] in 'child':
                properties[ns_]['variables'][key]['scope'] = 'bridge'
        for key in list(properties[ns_]['functions'].keys()):
            if properties[ns_]['functions'][key]['scope'] in 'local parent':
                del properties[ns_]['functions'][key]
            elif properties[ns_]['functions'][key]['scope'] in 'child':
                properties[ns_]['functions'][key]['scope'] = 'bridge'

    top_local_key_list = []
    process_value.current_local_key_list = top_local_key_list
    file_data = load_yaml_to_FlexiDict(file_name)
    # print(file_data)

    # print('before: ',properties, '\n')

    # Process variables and functions in the current file
    # print(file_data)
    for position, define_key in enumerate(file_data.keys()):
        if 'variables' == define_key:
            for key, value in file_data[position][1] if file_data[position][1] is not None else []:
                tag = key.split('/')
                name = process(tag[0])
                scope = process(tag[1] if len(tag) == 2 else 'local')
                if scope not in 'local parent child global'.split():
                    raise ValueError(f"The scope of variable '{name}' is wrong! 'local parent child global' are allowed")
                # if name in properties['default']['variables'].keys():
                #     if properties['default']['variables'][name]['scope'] in 'arg justpass bridge'.split():
                #         raise ValueError(f"The variable '{name}' is already defined!")
                # if (temp['default']['variables'][name]['scope'] in 'child parent' and scope in 'parent global') if name in temp['default']['variables'].keys() else False:
                #     raise ValueError(f"The variable '{name}' is already defined!")
                if '.' in key:
                    raise ValueError(f"The variable '{name}' cannot contain dots.")
                if name not in properties['default']['variables'] or properties['default']['variables'][name]['scope'] not in ['arg', 'justpass', 'bridge']:
                    properties['default']['variables'][name] = {'value': process(value), 'scope': scope}
                if properties['default']['variables'][name]['scope'] == 'justpass' and scope in 'parent global'.split():
                    properties['default']['variables'][name]['scope'] = scope #newly added. review this!
        elif 'functions' == define_key:
            for key, value in file_data[position][1] if file_data[position][1] is not None else []:
                tag = key.split('/')
                name = process(tag[0])
                scope = process(tag[1] if len(tag) == 2 else 'local')
                if scope not in 'local parent child global'.split():
                    raise ValueError(f"The scope of function '{name}' is wrong! 'local parent child global' are allowed")
                if name in properties['default']['functions'].keys():
                    raise ValueError(f"The function '{name}' is already defined!")
                # if (temp['default']['functions'][name]['scope'] in 'child parent' and scope in 'parent global') if name in temp['default']['functions'].keys() else False:
                #     raise ValueError(f"The function '{name}' is already defined!")
                if '.' in key:
                    raise ValueError(f"The function '{name}' cannot contain dots.")
                if not name[0].isupper():
                    raise ValueError(f"The function '{name}' must start with a capital letter!")
                properties['default']['functions'][name] = {'value': value, 'scope': scope}

        elif 'import' ==  define_key:
            for value in file_data[position][1] if file_data[position][1] is not None else []:
                lib = process(value)
                process(f'$(import {lib})')











    def process_level(layer: list, local_key_list: list):
        global ite
        ite += 1
        local_key_list = []
        process_value.current_local_key_list = local_key_list

        for item in layer if layer is not None else []:
            item[0] = process(item[0])################## still not sure if its good idea to change the original yaml read data
            # print(file_data)

            # print('ite: ', ite, "prop: ", properties['default']['variables'])
            match item[0]:
                case 'part':
                    part_process(copy.deepcopy(item[1]), local_key_list, process_level)
                case 'process':
                    process(f'$({item[1]})')
                case 'print':
                    # print(properties)
                    # ANSI escape codes for colors
                    GREEN = "\033[32m"
                    RESET = "\033[0m"  # Reset color to default
                    print(f'{GREEN}user_print:{RESET} {process(item[1])}')
                case 'include':
                    try:
                        if len(item[1]['namespace']) > 1:
                            raise ValueError(f"Duplicates of defining the namespace in include found. it can only be defined once for inclusion.")
                        if len(item[1]['path']) > 1:
                            raise ValueError(f"Duplicates of defining the path in include found. it can only be defined once for inclusion.")
                        namespace = process(item[1]['namespace'][-1] if 'namespace' in item[1].keys() else 'default')
                        if not namespace[0].isupper() and namespace != 'default': #default namespace is the only namespace that is lowercase and is accessible directly
                            raise ValueError(f"The namespace '{item[1]['namespace'][-1]}' must start with a capital letter!")
                        path = process(item[1]['path'][-1])
                        if path in yaml_path_list:
                            raise Exception("path included is already used and it will cuase infinite recursion!")
                        copy_of_properties_to_pass = copy.deepcopy(properties)
                        for key_ in item[1].keys():
                            if len(item[1][key_]) > 1:
                                raise Exception(f'Duplicates of defining the variable {key_} found. It can only be defined once for inclusion.')
                            if key_ != 'path' and key_ != 'namespace':
                                copy_of_properties_to_pass['default']['variables'][key_] = {'scope': 'justpass', 'value': process(item[1][key_][-1])}
                        #the line beneath won't work when namespace is not default and not yet defined because **properties[namespace] is simply non existent and reading it will fail
                        #here I need to implement the logic of only merging values that are global, parent, bridge. ONLY THE VALUES, NOT THE SCOPE!
                        # properties[namespace] = {**properties[namespace], **process_yaml_to_urdf(a, copy.deepcopy(properties))['default']}
                        #if returned variable is bridge scope 
                        returned_properties = process_yaml_to_urdf(path, copy_of_properties_to_pass, (copy.deepcopy(yaml_path_list)).append(path))
                        if namespace not in properties:
                            properties[namespace] = dict(variables = dict(), functions = dict())
                        for key in returned_properties['default']['variables'].keys():
                            if key in properties[namespace]['variables'].keys():
                                if properties[namespace]['variables'][key]['scope'] == 'local':
                                    properties[namespace]['variables'][key] = returned_properties['default']['variables'][key]
                                else:
                                    properties[namespace]['variables'][key]['value'] = returned_properties['default']['variables'][key]['value']
                            elif 'justpass' != returned_properties['default']['variables'][key]['scope']:
                                properties[namespace]['variables'][key] = returned_properties['default']['variables'][key]

                        for key in returned_properties['default']['functions'].keys():
                            if key in properties[namespace]['functions'].keys():
                                if properties[namespace]['functions'][key]['scope'] == 'local':
                                    properties[namespace]['functions'][key] = returned_properties['default']['functions'][key]
                                else:
                                    properties[namespace]['functions'][key]['value'] = returned_properties['default']['functions'][key]['value']
                            elif 'justpass' != returned_properties['default']['functions'][key]['scope']:
                                properties[namespace]['functions'][key] = returned_properties['default']['functions'][key]
                                
                        for returned_ns in returned_properties.keys(): #get returned properties's namespaces. merge them to the current properties
                            if returned_ns != 'default':
                                for key in returned_properties[returned_ns]['variables'].keys():
                                    if key in properties[returned_ns]['variables'].keys():
                                        if properties[returned_ns]['variables'][key]['scope'] == 'local':
                                            properties[returned_ns]['variables'][key] = returned_properties[returned_ns]['variables'][key]
                                        else:
                                            properties[returned_ns]['variables'][key]['value'] = returned_properties[returned_ns]['variables'][key]['value']
                                    elif 'justpass' != returned_properties[returned_ns]['variables'][key]['scope']:
                                        properties[returned_ns]['variables'][key] = returned_properties[returned_ns]['variables'][key]

                                for key in returned_properties[returned_ns]['functions'].keys():
                                    if key in properties[returned_ns]['functions'].keys():
                                        if properties[returned_ns]['functions'][key]['scope'] == 'local':
                                            properties[returned_ns]['functions'][key] = returned_properties[returned_ns]['functions'][key]
                                        else:
                                            properties[returned_ns]['functions'][key]['value'] = returned_properties[returned_ns]['functions'][key]['value']
                                    elif 'justpass' != returned_properties[returned_ns]['functions'][key]['scope']:
                                        properties[returned_ns]['functions'][key] = returned_properties[returned_ns]['functions'][key]



                        process_value.current_properties = properties

                    except Exception as e:
                        raise Exception(f"Error processing file '{item[1]['path']}'. {e}")

                case 'for':
                    try:
                        iterator = process(item[1]['iterator'][0])
                        range_ = split_(process(str(item[1]['range'][0])))


                        if len(range_) == 1:
                            range_.append(range_[0])
                            range_[0] = 0
                            range_.append(1)
                        elif len(range_) == 2:
                            range_.append(1)

                        for t in range(int(range_[0]), int(range_[1]), int(range_[2])):
                            process(f'$({iterator} = {t})')
                            # print(pretty_print_dict(properties))
                            process_level(item[1]['body'][-1], local_key_list)
                    except Exception as e:
                        raise Exception(f"Error processing for loop. {e}")

                case 'if':
                    # print(properties['default']['variables'])
                    try:
                        condition = process(f'$({item[1]['condition'][0]})')
                        # print(item[1]['condition'][0])
                        # print(condition)
                        if (eval(condition)):
                            process_level(item[1]['body'][-1], local_key_list)
                    except Exception as e:
                        raise Exception(f"Error processing if. {e}")
                case _:
                    if item[0][0].isupper():  #function                      
                        def CallFunction(ns, function_name):
                            function_args = []
                            # print(properties['default'])
                            # print()
                            # print(process((properties[ns]['functions'][function_name]['value'])['input'][-1]))
                            # print()
                            # print(f"aaaaa {function_name}: ", (properties[ns]['functions'][function_name]['value'])['input'][-1])
                            # print()
                            # print(item)
                            function_inputs = process((properties[ns]['functions'][function_name]['value'])['input'][-1] if (properties[ns]['functions'][function_name]['value'])['input'][-1] is not None else '').split(',')
                            passed_param_list = []

                            for param in function_inputs:
                                if '**' in param:
                                    if (param.replace('*', '').strip() not in list(properties[ns]['functions'].keys())):
                                        if ((param.replace('*', '').strip())[0]).isupper():
                                            function_args.append(param.replace('*', '').strip())
                                        else:
                                            raise ValueError(f"The function parameter '{param}' has to have a name that starts with an uppercase letter.")
                                    else:
                                        raise ValueError(f"The function parameter '{param}' is defined already!.")

                            if item[1] is not None:
                                for key in item[1].keys():
                                    processed_key = process(key)
                                    if processed_key in function_args:
                                        value = FlexiDict()
                                        value.add('input', None)
                                        value.add('body', item[1][key][-1])
                                        properties[ns]['functions'][processed_key] = {'value': value, 'scope': 'local'}
                                    else:
                                        passed_param_list.append(processed_key)
                                        process(f'$({processed_key} = "{process(item[1][key][-1])}")')
                                                                            
                            for param in function_inputs:
                                if '=' in param:
                                    if param.split('=')[0].strip() not in passed_param_list:
                                        process(f'$({param.split("=")[0].strip()} = "{process(param.split("=")[1].strip())}")')

                            # print('hiiiiiiii: ', (properties[ns]['functions'][function_name]['value'])['body'][-1])
                            process_level((properties[ns]['functions'][function_name]['value'])['body'][-1], local_key_list)
                            for argument_funciton in function_args:
                                del properties[ns]['functions'][argument_funciton] #delete the passed function in its namespace because its supposed to be temporary!!!!

                        tag = item[0].split('.')
                        if len(tag) == 2 and tag[0] in properties.keys(): #if namespace is defined
                            if tag[1] in properties[tag[0]]['functions'].keys():
                                CallFunction(tag[0], tag[1])
                            else:
                                raise KeyError(f"The function '{tag[1]}' is not defined in namespace '{tag[0]}'. Ensure that the function is defined in the same namespace or use default namespace.")

                        elif len(tag) == 1 and tag[0] in properties['default']['functions'].keys():
                            CallFunction('default', tag[0])

                        else:
                            raise ValueError(f"The '{tag}' is causing syntax error. For calling function, ensure that it is defined. If you specified namespace, use namespace.my_function to resolve it. Namespaces cannot be nested!")
                    else:
                        ele_att = item[0].split('/')
                        att = {}
                        if len(ele_att) > 1 and ele_att[1] != '':
                            attributes = ele_att[1].split(',')
                            for attribute in attributes:
                                attribute = attribute.lstrip()
                                if ':' in attribute:
                                    att[attribute.split(':')[0]] = attribute.split(':')[1]
                                elif ':=' in attribute:
                                    att[attribute.split(':=')[0]] = attribute.split(':=')[1]
                                else:
                                    att[attribute.split('=')[0]] = attribute.split('=')[1]
                            # Capture 'item' by value in the lambda's default parameters
                        # print(type(item[1]))
                        if isinstance(item[1], FlexiDict) or isinstance(item[1], dict) or isinstance(item[1], list) or item[1] is None:
                            xml(
                                ele_att[0],
                                att,
                                [lambda item1=item[1], local_key_list=local_key_list: process_level(item1, local_key_list)]
                            )
                        else:
                            argument = ''.join(' {key}="{value}"'.format(key=key, value=str(att[key]).strip('\'"')) for key in att)
                            add_line_to_urdf('<{element}{argument}>{v}</{element}{argument}>'.format(element=ele_att[0], argument=argument, v=process(item[1])))




                    




        for key in local_key_list:
            if key in properties['default']['variables'].keys() and properties['default']['variables'][key]['scope'] == 'local':
                del properties['default']['variables'][key]
        process_value.current_local_key_list = local_key_list




    process_level(file_data['model'][-1], top_local_key_list)
    # print('after: ',properties, '\n')

    for ns_ in properties.keys():
        for key in list(properties[ns_]['variables'].keys()):
            
            if properties[ns_]['variables'][key]['scope'] in 'local child'.split():
                del properties[ns_]['variables'][key]
            elif properties[ns_]['variables'][key]['scope'] in 'parent'.split():
                properties[ns_]['variables'][key]['scope'] = 'bridge'

        for key in list(properties[ns_]['functions'].keys()):
            if properties[ns_]['functions'][key]['scope'] in 'local child'.split():
                del properties[ns_]['functions'][key]
            elif properties[ns_]['functions'][key]['scope'] in 'parent'.split():
                properties[ns_]['functions'][key]['scope'] = 'bridge'

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


def main(yamaro_file, *args) -> str:
    yamaro_file = os.path.expanduser(yamaro_file)

    properties = dict(default=dict(variables=dict(), functions=dict()))

    for idx, arg in enumerate(args):
        # print(f"Argument {idx}: {arg}")
        name, value = arg.split(':=')
        process(f'$({name} = {value})')
        properties['default']['variables'][name] = {'value': eval(value), 'scope': 'arg'}
        # print(properties)



    if 'robot' in load_yaml_to_FlexiDict(yamaro_file).keys():
        add_line_to_urdf(f'<robot name="{process(load_yaml_to_FlexiDict(yamaro_file)['robot'][0])}">')
    else:
        add_line_to_urdf(f'<robot name="default">')
    tab_()
    xml('link', {'name': 'root_link'})


    # print(load_yaml_to_FlexiDict(os.path.expanduser(sys.argv[1])))

    process_value.current_properties = properties
    # print(f'\n{BLUE}starting processing yaml to urdf!{RESET}\n')

    # process input arg so it allows passing variables! for now I will pass barebone properties
    process_yaml_to_urdf(yamaro_file, properties, [yamaro_file])
    untab_()
    add_line_to_urdf('</robot>')


    # print(f'\n\n{BLUE}output urdf:{RESET}\n{urdf_output}')

    return urdf_output

def convert(yamaro_file, *args) -> str:
    return main(yamaro_file, *args)


if __name__ == '__main__':
    output = main(sys.argv[1], *sys.argv[2:] if len(sys.argv) > 2 else [])
    with open('output.urdf', 'w') as f:
        f.write(output)