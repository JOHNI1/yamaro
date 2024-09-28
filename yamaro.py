from ament_index_python.packages import get_package_share_directory
from flexidict import load_yaml_to_FlexiDict
import sys


def Process_yaml_to_urdf(yaml_file_path):
    data = load_yaml_to_FlexiDict(yaml_file_path)
    return data
    variables = dict()
    # print(data)
    # print(data['variables'])
    # for variable in data['variables']:
    #     pass


    # local = {}


yaml_file_path = sys.argv[1]
print(Process_yaml_to_urdf(yaml_file_path))

print()
print()

x = Process_yaml_to_urdf(yaml_file_path)
print(x['body'][0])

print()
print()

for component in x['body'][0]:
    key = component[0].split('/')
    if 'include' == key[0]:
        print(component)

