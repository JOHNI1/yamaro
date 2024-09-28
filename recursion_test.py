import os
from ament_index_python.packages import get_package_share_directory
from flexidict import load_yaml_to_FlexiDict
from process_value import process_value

urdf_output = ''




def process_yaml(file_name, properties):
    local_vars = []
    file_data = load_yaml_to_FlexiDict(os.path.expanduser(file_name))

    # Process variables in the current file
    for key, value in file_data['variables'][0]:
        if '/' in key:
            name, scope = key.split('/')
            properties['default']['variables'][name] = {'value': process_value(value, properties), 'scope': scope}
        else:
            properties['default']['variables'][key] = {'value': process_value(value, properties), 'scope': 'local'}
        
    for var_scope, value in file_data['functions'][0]:
        var, scope = var_scope.split('/')
        var_store.set_variable(var, value, scope)

    # Process body if exists
    body=None
    try:
        body = file_data['body'][0]
    except:
        pass
    
    for component in body:
        if 'include' == component[0]:
            print(component)
            child_store = VariableStore()
            process_yaml(component[1]['path'][0], child_store, var_store, namespace=(component[1]['namespace'][0] if 'namespace' in component[1] else None))


        if 'process' in body:
            # Evaluate the process field using the variables
            local_vars = {**var_store.global_, **var_store.local}
            if parent_store:
                local_vars.update(parent_store.parent)
            local_vars.update(var_store.child)
            local_vars.update(var_store.parent)

            # Include all namespaces into the local vars for process execution
            local_vars.update(var_store.namespaces)
            
            eval(body['process'], {}, local_vars)

    # After recursion, propagate variables back to the parent if needed
    if parent_store:
        for var, value in var_store.parent.items():
            parent_store.set_variable(var, value, 'parent')
        for var, value in var_store.global_.items():
            parent_store.set_variable(var, value, 'global')

    print(f"file_name: {file_name}, local, {get_variable}")


# Start with the first YAML file and a global variable store
properties = dict(default=dict(functions=dict(), variables=dict()))
print(properties['default'])
# process_yaml('example.yaml', properties)

# Example of accessing global variables after processing
