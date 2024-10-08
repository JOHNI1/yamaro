# Yamaro

## Overview

Yamaro is a YAML-based templating engine designed to generate URDF (Unified Robot Description Format) files or other XML-based outputs. It allows users to define robot models using a flexible syntax that supports custom elements, attributes, variables with different scopes, conditionals, loops, functions, and importing other YAML files with namespace support.

---

## Features

- **Define Robot Parts**: Easily define robot parts with joints and links.
- **Custom XML Elements**: Create custom XML elements with attributes and nested content.
- **Variables with Scopes**: Use variables with different scopes (`local`, `global`, `parent`, `child`).
- **Functions**: Define reusable code blocks with parameters.
- **Importing Modules**: Import Python modules directly within your YAML file.
- **Control Structures**: Implement logic using `if` statements and iterate with `for` loops.
- **Printing**: Output messages during processing for debugging or information.
- **Command-Line Arguments**: Pass variables to the script when launching.

---

## Installation

To use Yamaro, ensure you have Python 3 installed along with the required dependencies. You can install the necessary packages using `pip`:

```bash
pip install flexidict process_value pretty_print_dict ament_index_python
```

---

## Syntax and Usage

### YAML Syntax in Yamaro

- **Lists and Duplicate Keys**: Yamaro uses a custom class (`FlexiDict`) to handle duplicate keys and lists. You can define lists using the `-` character or by repeating keys.

**Example of Defining a List in Variables**:

```yaml
variables:
  my_list:
    - a
    - b
    - c
```

Accessing `$(my_list)` will output: `['a', 'b', 'c']`

---

### Defining Variables

Variables are declared under the `variables` section and can hold values such as numbers, strings, or lists. Variables can have scopes:

- **`local`**: Available only within the current context.
- **`global`**: Available throughout the entire script.
- **`parent`**, **`child`**: Control variable availability in included files or functions.

**Syntax**:

```yaml
variables:
  variable_name[/scope]: value
```

- The `/scope` is optional and defaults to `local` if not specified.

**Examples**:

```yaml
variables:
  arm_length/global: 1.0
  base_width: 0.5  # Defaults to 'local' scope
  my_list:
    - item1
    - item2
    - item3
```

---

### Defining a Function

Functions allow you to define reusable code blocks with parameters.

**Function Definition Syntax**:

```yaml
functions:
  FunctionName[/scope]:
    input: param1, param2=value
    body:
      # Function content
```

- **`FunctionName`**: Must start with an uppercase letter.
- **`/scope`**: Optional; if omitted, defaults to `local`.
- **`input`**: Parameters the function accepts, with optional default values.
- **`body`**: The content executed when the function is called.

**Example Definition**:

```yaml
functions:
  CreateArm/local:
    input: name, length=1.0
    body:
      part:
        name: $(name)
        joint:
          type: revolute
          parent: base_link
          xyz: 0 0 0
          rpy: 0 0 0
        link:
          xyz: 0 0 0
          rpy: 0 0 0
          geometry: box
          scale: $(length) 0.1 0.1
          mass: 0.5
          collision:
          visual:
          inertial:
```

**Function Call Syntax**:

```yaml
FunctionName:
  param1: value1
  param2: value2
```

**Example Calls**:

```yaml
CreateArm:
  name: arm_left
  length: 1.2

CreateArm:
  name: arm_right
```

---

### Defining a Part

A `part` represents a component of the robot and includes:

- **`name`**: The name of the part (defines both joint and link names).
- **`joint`**: Defines the joint connecting this part to its parent.
  - **`type`**: The type of joint (e.g., `fixed`, `revolute`).
  - **`parent`**: The name of the parent link.
  - **`xyz`**: The position of the joint.
  - **`rpy`**: The orientation of the joint.
  - **Additional Joint Elements**: Any additional URDF joint elements can be included.
- **`link`**: Defines the link associated with the part.
  - **`xyz`**, **`rpy`**: The position and orientation of the link itself.
  - **`geometry`**: The shape of the link (e.g., `box`, `cylinder`, `sphere`, or mesh file).
  - **`scale`**: The dimensions of the geometry.
  - **`mass`**: The mass of the link.
  - **`inertial`**: Inertial properties of the link.
  - **`collision`**: Collision properties.
  - **`visual`**: Visual properties.
  - **Additional Link Elements**: Any additional URDF link elements can be included.

**Notes on `collision`, `visual`, and `inertial` Tags**:

- You can include multiple `collision`, `visual`, and `inertial` tags within a `link`.
- These tags can be left empty to inherit defaults or specify properties within them.
- Properties specified inside `collision`, `visual`, or `inertial` will override those specified in the parent `link`.

**Positioning**:

- The `xyz` and `rpy` under `link` set the base position and orientation.
- Positions specified within `collision`, `visual`, or `inertial` are relative to the `link`'s position and are added to it.

**Example**:

```yaml
part:
  name: wheel
  joint:
    type: continuous
    parent: base_link
    xyz: 1 0 0
    rpy: 0 0 0
  link:
    xyz: 0 0 0.1
    rpy: 0 0 0
    geometry: cylinder
    scale: 0.5 0.2
    mass: 1.0
    inertial:
      geometry: tube
      scale: 0.51 0.2
    collision:
    visual:
```

In this example:

- The `inertial` tag includes a different `geometry` and `scale` for inertia calculations.
- Empty `collision` and `visual` tags will inherit the geometry and scale from the parent `link`.

---

### Importing Other YAML Files

You can import other YAML files to reuse common parts or functions. Imported files can have their own namespace to avoid naming conflicts.

**Syntax**:

```yaml
import:
  - module_name
```

- **`module_name`**: The name of the Python module to import (e.g., `math`, `numpy`).

**Example**:

```yaml
import: 
  - math
  - ament_index_python.packages
```

This will import the `math` module and the `ament_index_python.packages` module, allowing you to use their functions and constants within your YAML file.

---

### Control Structures

#### If Statements

Use `if` statements to conditionally execute sections of the code based on expressions.

**Syntax**:

```yaml
if:
  condition: expression
  body:
    # Content to execute if condition is true
```

**Example**:

```yaml
if:
  condition: $(arm_length) > 0.5
  body:
    print: Long arm detected.
```

---

#### For Loops

Iterate over ranges using `for` loops.

**Syntax**:

```yaml
for:
  iterator: variable_name
  range: <start (optional)>, <stop>, <step (optional)>
  body:
    # Content to repeat
```

- **`iterator`**: The loop variable name.
- **`range`**:
  - If only one value is provided, it is treated as the stop value with a default start of `0` and step of `1`.
  - If two values are provided, they are treated as start and stop with a default step of `1`.
  - If three values are provided, they are treated as start, stop, and step.

**Examples**:

- **Using `range` with `stop` only**:

  ```yaml
  for:
    iterator: i
    range: 5
    body:
      print: Iteration $(i)
  ```

  This will iterate `i` from `0` to `4`.

- **Using `range` with `start` and `stop`**:

  ```yaml
  for:
    iterator: i
    range: 1, 5
    body:
      print: Iteration $(i)
  ```

  This will iterate `i` from `1` to `4`.

- **Using `range` with `start`, `stop`, and `step`**:

  ```yaml
  for:
    iterator: i
    range: 0, 10, 2
    body:
      print: Iteration $(i)
  ```

  This will iterate `i` over `0, 2, 4, 6, 8`.
  
---

### Printing

Use `print` to output messages during processing. This is useful for debugging or providing information.

**Syntax**:

```yaml
print: message
```

**Example**:

```yaml
print: Building robot with arm length $(arm_length).
```

This will output: `user_print: Building robot with arm length 1.5.`

---

### Process Statements

Use `process` to execute arbitrary Python code. This allows for more advanced operations such as importing additional modules or running functions.

**Syntax**:

```yaml
process: python_code
```

**Example**:

```yaml
process: import numpy
```

This will execute the Python code `import numpy`, making the `numpy` module available for use in subsequent expressions.

---

### Importing Python Modules

You can import Python modules within your YAML file to use their functions and constants in expressions.

**Example**:

```yaml
import: 
  - math
  - ament_index_python.packages
```

This allows you to use `math.pi` or functions from `ament_index_python.packages` in your variables or expressions.

---

### Command-Line Arguments

You can pass variables to the Yamaro script directly from the command line. These variables are immediately available in your YAML file and can be used directly in expressions.

**Command-Line Syntax**:

```bash
python3 yamaro.py input.yaml variable1:=value1 variable2:=value2
```

**Example Command**:

```bash
python3 yamaro.py robot.yaml arm_length:=1.5
```

**YAML Usage**:

```yaml
print: The arm length is $(arm_length).
```

In this example, `$(arm_length)` will be replaced with the value `1.5` that was passed from the command line. You don't need to define `arm_length` in the `variables` section of your YAML file when passing it via the command line.

---

## Complete Example

**Command Line**:

```bash
python3 yamaro.py drone.yaml
```

**drone.yaml**:

```yaml
robot: drone

import: 
  - math
  - ament_index_python.packages

variables:
  pi: $(math.pi)
  right: $(pi/2)
  x: $(dict(a=1, b=2, c=3))
  y: {'a': 1, 'b': 2, 'c': 3}

functions:
  MakePart:
    input: name, type, parent, xyz, rpy, geometry, scale, **Block_To_Insert
    body:
      part:
        name: $(name)
        joint:
          type: $(type)
          parent: $(parent)
          xyz: $(xyz)
          rpy: $(rpy)
          Block_To_Insert:
        link:
          geometry: $(geometry)
          scale: $(scale)
          mass: 10
          collision:
            Block_To_Insert:
          visual:
            Block_To_Insert:
          inertial:
            Block_To_Insert:
          Block_To_Insert:

model:
  process: print_properties()
  process: import numpy
  print: $(right)
  print: $(x['a'])
  print: $(1+pi)
  print: $(y['a'])

  for:
    iterator: i
    range: 1
    body:
      gazebo/name=part$(i):
        a: 1
      MakePart:
        name: part$(i)
        type: fixed
        parent: root_link
        xyz: '$(i) $(i) $(i)'
        rpy: '$(i) $(i) $(i)'
        geometry: sphere
        scale: '1'
        Block_To_Insert:
          gazebo/xyz=1 1 1:
            a: 1
```

**Expected Output**:

```
Argument 0: yamaro.py
Argument 1: drone.yaml

starting processing yaml to urdf!

print_properties: {'default': {'variables': {'pi': {'value': '3.141592653589793', 'scope': 'local'}, 'right': {'value': '1.5707963267948966', 'scope': 'local'}, 'x': {'value': "{'a': 1, 'b': 2, 'c': 3}", 'scope': 'local'}, 'y': {'value': {'a': 1, 'b': 2, 'c': 3}, 'scope': 'local'}}, 'functions': {'MakePart': {'value': [
  ['input', 'name, type, parent, xyz, rpy, geometry, scale, **Block_To_Insert'],
  ['body', [
    ['part', [
      ['name', '$(name)'],
      ['joint', [
        ['type', '$(type)'],
        ['parent', '$(parent)'],
        ['xyz', '$(xyz)'],
        ['rpy', '$(rpy)'],
        ['Block_To_Insert', None],
      ]],
      ['link', [
        ['geometry', '$(geometry)'],
        ['scale', '$(scale)'],
        ['mass', 10],
        ['collision', [
          ['Block_To_Insert', None],
        ]],
        ['visual', [
          ['Block_To_Insert', None],
        ]],
        ['inertial', [
          ['Block_To_Insert', None],
        ]],
        ['Block_To_Insert', None],
      ]],
    ]],
  ]],
], 'scope': 'local'}}}}
user_print: 1.5707963267948966
user_print: 1
user_print: 4.141592653589793
user_print: 1

output urdf:
<?xml version="1.0" ?>
<robot name="drone">
  <link name="root_link"/>
  <gazebo name="part0">
    <a>1</a>
  </gazebo>
  <joint name="part0_joint" type="fixed">
    <origin xyz="0 0 0" rpy="0 0 0"/>
    <parent link="root_link"/>
    <child link="part0_link"/>
    <gazebo xyz="1 1 1">
      <a>1</a>
    </gazebo>
  </joint>
  <link name="part0_link">
    <collision>
      <geometry>
        <sphere radius="1.0"/>
      </geometry>
      <origin xyz="0 0 0" rpy="0 0 0"/>
      <gazebo xyz="1 1 1">
        <a>1</a>
      </gazebo>
    </collision>
    <visual>
      <geometry>
        <sphere radius="1.0"/>
      </geometry>
      <origin xyz="0 0 0" rpy="0 0 0"/>
      <gazebo xyz="1 1 1">
        <a>1</a>
      </gazebo>
    </visual>
    <inertial>
      <mass value="10"/>
      <origin xyz="0 0 0" rpy="0 0 0"/>
      <inertia ixx="4.0" ixy="0" ixz="0" iyy="4.0" iyz="0" izz="4.0"/>
      <gazebo xyz="1 1 1">
        <a>1</a>
      </gazebo>
    </inertial>
    <gazebo xyz="1 1 1">
      <a>1</a>
    </gazebo>
  </link>
</robot>
```

---

## Additional Notes on `link`, `collision`, `visual`, and `inertial` Tags

- **Including `inertial` Elements**:
  - In the example above, we explicitly include the `inertial` tag within the `link`. This ensures that the inertial properties are included in the generated URDF.
  - If the `inertial` tag is not specified, Yamaro will not generate an `<inertial>` element in the output.

- **Customization**:
  - Inside each `collision`, `visual`, or `inertial` tag, you can specify properties like `geometry`, `scale`, `mass`, `xyz`, and `rpy` to override the defaults.
  - For example, you might specify a different geometry inside `inertial` to calculate the inertia based on a different shape.

- **Positioning**:
  - The `xyz` and `rpy` under `link` set the base position and orientation.
  - Positions specified within `collision`, `visual`, or `inertial` are relative to the `link`'s position and are added to it.
  - This allows for precise positioning of visual and collision elements relative to the link.

**Example with Customized `inertial`**:

```yaml
link:
  name: custom_link
  xyz: 0 0 0
  rpy: 0 0 0
  geometry: box
  scale: 1 1 1
  mass: 2.0
  inertial:
    geometry: cylinder
    scale: 0.5 0.5
    mass: 1.5
    xyz: 0 0 0.5
    rpy: 0 0 0
  collision:
    geometry: box
    scale: 1 1 1
  visual:
    geometry: box
    scale: 1 1 1
```

In this example:

- The `inertial` tag has its own `geometry`, `scale`, `mass`, `xyz`, and `rpy`, overriding the defaults from the `link`.
- The positions of `collision` and `visual` are relative to the `link`'s position.
- This flexibility allows you to fine-tune each aspect of the link's properties.

---

## Running the Script

Run the Yamaro script with your YAML file:

```bash
python3 yamaro.py robot.yaml
```

Or pass variables directly:

```bash
python3 yamaro.py robot.yaml length:=1.5
```

---

## Notes

- **Expressions**: Use `$(...)` to evaluate expressions or access variables (e.g., `$(length)`).
- **String Values**: Enclose expressions or values containing operators or special characters in quotes.
- **Namespaces**: Use namespaces to organize functions and prevent naming conflicts when importing other YAML files.
- **Scopes**: Be mindful of variable scopes (`local`, `global`, `parent`, `child`) to control visibility.
- **Custom Parsing**: Yamaro uses custom parsing to handle the unique YAML syntax.
- **Function Naming**: Functions must start with an uppercase letter and should not contain dots unless specifying a namespace (e.g., `Namespace.FunctionName`).

---

## Conclusion

I apologize again for the confusion earlier. Variables passed from the command line are available directly in your YAML file without needing to redefine them. You can use them immediately in your expressions and code.

Yamaro provides a powerful and flexible way to define robot models using a YAML syntax tailored for hierarchical and repetitive structures. By leveraging features like customizable `collision`, `visual`, and `inertial` tags, importing modules, and defining functions, you can precisely control the properties of each link in your robot model.

Feel free to explore Yamaro's features and customize your robot models according to your needs!

---
