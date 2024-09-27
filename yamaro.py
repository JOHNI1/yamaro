from ament_index_python.packages import get_package_share_directory
from flexidict import FlexiDict, load_yaml_to_FlexiDict

pkg_name = 'drone'
pkg_path = get_package_share_directory(pkg_name)

print(pkg_path)

print()

print(load_yaml_to_FlexiDict('example.yaml'))


# def main:
    # Your code here