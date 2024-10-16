
# Yamaro

## Overview

Yamaro is a YAML-based templating engine designed to generate URDF (Unified Robot Description Format) files or other XML-based outputs. It allows users to define robot models using a flexible syntax that supports custom elements, attributes, variables with different scopes, conditionals, loops, functions, and importing other YAML files with namespace support.

---

## Features

- **Define Robot Parts**: Easily define robot parts with joints and links.
- **Custom XML Elements**: Create custom XML elements with attributes and nested content.
- **Variables with Scopes**: Use variables with different scopes (`local`, `global`, `parent`, `child`).
- **Functions**: Define reusable code blocks with parameters, and pass snippets of code to them.
- **Importing Modules**: Import Python modules directly within your YAML file.
- **Control Structures**: Implement logic using `if` statements and iterate with `for` loops (supports Python-style range).
- **Printing**: Output messages during processing for debugging or information.
- **Command-Line Arguments**: Pass variables to the script when launching.

---

## Installation

Option 1: System-Wide Installation

```bash
  git clone https://github.com/JOHNI1/yamaro.git
  cd yamaro
  sudo python3 -m pip install . --break-system-packages
```

Option 2: Virtual Environment Installation (Recommended)

```bash
  git clone https://github.com/JOHNI1/yamaro.git
  cd yamaro
  python3 -m venv venv
  source venv/bin/activate
  pip install .
```

To uninstall:
```bash
  sudo python3 -m pip uninstall yamaro --break-system-packages
```

---

## Usage

import yamaro

```python
  output = yamaro.convert('input.yaml')
  with open('output.urdf', 'w') as f:
      f.write(output)
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

### Defining a Function and Passing Code Snippets

Functions allow you to define reusable code blocks with parameters and can also accept snippets of code that will be evaluated when the function is called.

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
- **`body`**: The content executed when the function is called. This can include other YAML definitions and code snippets.

**Example Definition with Code Snippet**:

```yaml
functions:
  CreateArm/local:
    input: name, length=1.0, CodeBlock=None
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
      process: $(CodeBlock)  # Evaluates the passed code snippet
```

**Function Call Syntax**:

```yaml
FunctionName:
  param1: value1
  param2: value2
```

**Example Call with Code Snippet**:

```yaml
CreateArm:
  name: arm_left
  length: 1.2
  CodeBlock: |
    print: "Custom code inside function"
    process: print('Executing custom code...')
```

In this example, the function will process the code passed in `CodeBlock` during execution.

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

---

### Importing Other YAML Files

You can import other YAML files to reuse common parts or functions. Imported files can have their own namespace to avoid naming conflicts.

**Syntax**:

```yaml
import:
  - module_name
```

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

---

#### For Loops (Python-style `range`)

You can use `for` loops to iterate over ranges, just like in Python's `range()` function. You can specify `start`, `stop`, and `step` values, with default behaviors similar to Python.

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
  - If only one value is provided, it is treated as the stop value with a default start of `0` and step of `1`, just like in Python.
  - If two values are provided, they are treated as `start` and `stop`, with a default step of `1`.
  - If three values are provided, they are treated as `start`, `stop`, and `step`.

**Example**:

```yaml
for:
  iterator: i
  range: 0, 5, 1  # Just like Python's range function
  body:
    print: Iteration $(i)
```

This will print the loop variable `i` from `0` to `4` with a step of `1`.

---

### Printing

Use `print` to output messages during processing. This is useful for debugging or providing information.

**Syntax**:

```yaml
print: message
```

---

### Process Statements

Use `process` to execute arbitrary Python code. This allows for more advanced operations such as importing additional modules or running functions.

---

### Command-Line Arguments

You can pass variables to the Yamaro script directly from the command line. These variables are immediately available in your YAML file and can be used directly in expressions.

---

## Conclusion

Yamaro provides a powerful and flexible way to define robot models using YAML, with features like custom parts, loops, conditionals, and the ability to pass code snippets to functions for greater flexibility. With Python-style `range` loops and powerful templating capabilities, it's well-suited for complex URDF generation and more.
