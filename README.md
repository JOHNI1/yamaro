# Yamaro

## Overview

Yamaro is a YAML-based templating engine designed to generate URDF (Unified Robot Description Format) files or other XML-based outputs. It allows users to define robot models using a flexible syntax that supports:

- Custom elements and attributes
- Variables with different scopes
- Conditionals (with automatically evaluated conditions)
- Loops
- Functions (with code snippets passed using `**Block`)
- Importing Python libraries
- Including other YAML files within the model or function bodies
- Advanced mathematical expressions
- Custom scopes and variable passing between included files and functions

---

## Features

- **Define Robot Parts**: Easily define robot parts with joints and links.
- **Custom XML Elements**: Create custom XML elements with attributes and nested content.
- **Variables with Scopes**: Use variables with different scopes (`local`, `global`, `parent`, `child`, `bridge`).
- **Functions with Code Snippets**: Define reusable code blocks with parameters, and pass code snippets to them using `**Block`.
- **Importing Python Libraries**: Import Python modules directly within your YAML file.
- **Including Other YAML Files**: Include and reuse other YAML files within the model or function bodies.
- **Control Structures**: Implement logic using `if` statements (conditions are automatically evaluated) and iterate with `for` loops.
- **Printing and Process Statements**: Output messages during processing and execute Python code snippets.
- **Advanced Mathematical Expressions**: Perform complex calculations within variable assignments and expressions.
- **Command-Line Arguments**: Pass variables to the script when launching.

---

## Installation

### Option 1: System-Wide Installation

```bash
git clone https://github.com/JOHNI1/yamaro.git
cd yamaro
sudo python3 -m pip install . --break-system-packages
```

### Option 2: Virtual Environment Installation (Recommended)

```bash
git clone https://github.com/JOHNI1/yamaro.git
cd yamaro
python3 -m venv venv
source venv/bin/activate
pip install .
```

### To Uninstall:

```bash
sudo python3 -m pip uninstall yamaro --break-system-packages
```

---

## Usage

```python
import yamaro

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

- **`local`**: Available only within the current context (default if not specified).
- **`global`**: Available throughout the entire script and included files.
- **`parent`**, **`child`**: Control variable availability in included files or functions.
- **`bridge`**: Used internally to pass variables between included files and the main file.

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

### Variable Usage and Substitution

To use a variable within your YAML file, enclose it in `$()`. The expression inside `$()` is evaluated, and variables are substituted.

**Example**:

```yaml
print: "The arm length is $(arm_length)"
```

---

### Defining Functions and Passing Code Snippets

Functions allow you to define reusable code blocks with parameters and can accept code snippets that will be evaluated when the function is called.

**Function Definition Syntax**:

```yaml
functions:
  FunctionName[/scope]:
    input: param1, param2=value, **Block
    body:
      # Function content
      # Include the code block at the desired location using `Block:`
      # Other function content
```

- **`FunctionName`**: Must start with an uppercase letter.
- **`/scope`**: Optional; defaults to `local` if not specified.
- **`input`**: Parameters the function accepts, with optional default values.
  - Use `**Block` to accept a code snippet.
- **`body`**: The content executed when the function is called.
  - Include the code block at any point in the `body` by using `Block:` as a key.

**Example Function Definition with Code Snippet**:

```yaml
functions:
  CreateArm/local:
    input: name, length=1.0, **CodeBlock
    body:
      # Function content before the code block
      part:
        name: $(name)
        joint:
          type: revolute
          parent: base_link
          xyz: 0 0 0
          rpy: 0 0 0
        link:
          geometry: box
          scale: $(length) 0.1 0.1
          mass: 0.5
          collision:
          visual:
          inertial:
      # Include the code block at this point
      CodeBlock:
        # The code block will be inserted here when the function is called
      # Function content after the code block (optional)
```

**Function Call Syntax**:

```yaml
FunctionName:
  param1: value1
  param2: value2
  CodeBlock:
    # Code snippet to pass to the function
```

**Example Call with Code Snippet**:

```yaml
CreateArm:
  name: arm_left
  length: 1.2
  CodeBlock:
    # Custom code to include within the function
    print: "Custom code inside function"
    process: print("Executing custom code...")
```

**Explanation**:

- **Flexible Code Insertion**: Insert the code block anywhere within the function body by placing `Block:` at the desired location.
- **Customizable Functions**: Allows functions to be flexible and adaptable to different needs by accepting custom code.
- **Naming Consistency**: Ensure that the name of the code block parameter (`**CodeBlock`) matches the key used in the function body (`CodeBlock:`).

---

### Defining a Part

A `part` represents a component of the robot and includes:

- **`name`**: The name of the part (defines both joint and link names).
- **`joint`**: Defines the joint connecting this part to its parent.
  - **`type`**: The type of joint (e.g., `fixed`, `revolute`).
  - **`parent`**: The name of the parent link.
  - **`xyz`**: The position of the joint.
  - **`rpy`**: The orientation of the joint.
  - **`pivot`**: The pivot point for rotation.
  - **Additional Joint Elements**: Any additional URDF joint elements can be included.
- **`link`**: Defines the link associated with the part.
  - **`geometry`**: The shape of the link (e.g., `box`, `cylinder`, `sphere`, or mesh file).
  - **`scale`**: The dimensions of the geometry.
  - **`mass`**: The mass of the link.
  - **`xyz`**, **`rpy`**: The position and orientation of the link itself.
  - **`pivot`**: The pivot point for rotation.
  - **`collision`**, **`visual`**, **`inertial`**: Sections to define specific properties of the link.
    - **`collision`**: Defines the collision geometry of the link, used by the physics engine to detect collisions.
    - **`visual`**: Specifies the visual representation of the link, including its geometry and appearance when rendered in visualization tools.
    - **`inertial`**: Defines the physical properties of the link, such as mass and inertia tensor, which are essential for dynamic simulations.
  - **Additional Link Elements**: Any additional URDF link elements can be included.

#### The `collision`, `visual`, and `inertial` Sections

##### **`collision` Section**

- **Purpose**: Defines the collision geometry for the link, which the physics engine uses for collision detection.
- **Geometry**: Specifies the shape and dimensions used for collision calculations.
- **Optimization**: Often simplified compared to the visual geometry to improve simulation performance.
- **Syntax**:

  ```yaml
  collision:
    geometry: box
    scale: 0.5 0.5 0.5
    xyz: 0 0 0
    rpy: 0 0 0
    # Additional collision-specific elements can be added here
  ```

##### **`visual` Section**

- **Purpose**: Defines how the link appears visually, including geometry and material properties.
- **Geometry**: Specifies the shape, scale, and position used for rendering the link.
- **Material**: Allows you to define colors, textures, and other visual properties.
- **Syntax**:

  ```yaml
  visual:
    geometry: box
    scale: 0.5 0.5 0.5
    xyz: 0 0 0
    rpy: 0 0 0
    material:
      name: "Blue"
      color: 0 0 1 1  # RGBA values
    # Additional visual-specific elements can be added here
  ```

##### **`inertial` Section**

- **Purpose**: Defines the physical properties of the link, such as mass and inertia tensor.
- **Mass and Inertia**: Essential for dynamic simulations to calculate how forces affect the link.
- **Automatic Inertia Calculation**: If inertia is not provided, Yamaro can compute it based on the geometry and mass.
- **Syntax**:

  ```yaml
  inertial:
    mass: 1.0
    inertia: 0.1 0 0 0.1 0 0.1  # ixx, ixy, ixz, iyy, iyz, izz
    xyz: 0 0 0
    rpy: 0 0 0
    # Additional inertial-specific elements can be added here
  ```

#### Example of Defining a Part with `collision`, `visual`, and `inertial`

```yaml
part:
  name: wheel
  joint:
    type: continuous
    parent: base_link
    xyz: 1 0 0
    rpy: 0 0 0
    pivot: 0 0 0
  link:
    geometry: cylinder
    scale: 0.5 0.2  # radius and length
    mass: 1.0
    xyz: 0 0 0.1
    rpy: 0 0 0
    pivot: 0 0 0
    collision:
      geometry: cylinder
      scale: 0.5 0.2
      xyz: 0 0 0
      rpy: 0 0 0
    visual:
      geometry: cylinder
      scale: 0.5 0.2
      xyz: 0 0 0
      rpy: 0 0 0
      material:
        name: "Black"
        color: 0 0 0 1
    inertial:
      mass: 1.0
      inertia: 0.05 0 0 0.05 0 0.1
      xyz: 0 0 0
      rpy: 0 0 0
```

**Explanation**:

- **`collision` Section**:
  - Defines the collision geometry, critical for detecting collisions during simulation.
  - May be simplified to reduce computational load.
- **`visual` Section**:
  - Specifies the visual appearance, including geometry and material properties.
  - Material properties define the color and appearance in visualization tools.
- **`inertial` Section**:
  - Specifies the mass and inertia tensor of the link.
  - If the inertia tensor is not provided, Yamaro can calculate it based on the geometry and mass.

#### How Yamaro Processes These Sections

- **In `inertial`**:
  - Uses the provided mass and inertia tensor.
  - If inertia is not specified, computes it based on the geometry and mass.
  - Generates `<inertial>`, `<mass>`, `<origin>`, and `<inertia>` elements in URDF.

- **In `visual` and `collision`**:
  - Processes the geometry, scale, and transforms.
  - Generates `<visual>` and `<collision>` elements, each containing `<geometry>` and `<origin>` elements.
  - Material properties in `visual` are translated into `<material>` elements in URDF.

---

### Importing Python Libraries

You can import Python libraries directly within your YAML file. This is useful when you need to use functions or constants from external Python modules.

**Syntax**:

```yaml
import:
  - math
  - numpy
```

- The `import` section should be at the root level of your YAML file.
- Each library is specified as an item in the list.

**Usage**:

After importing, you can use the library in your expressions or code snippets. For example:

```yaml
variables:
  radius: 2.0
  circle_area: $(math.pi * radius ** 2)
print: "The area of the circle is $(circle_area)"
```

**Note**:

- In `process` statements, you **do not** need to wrap expressions with `$()`.
- Only use `$()` for variable substitution within strings or variable assignments.

---

### Including Other YAML Files within Model or Functions

You can include other YAML files to reuse common parts, variables, or functions. The `include` command is used **within the `model` section or inside function bodies**, not at the root level of the YAML file. Included files are processed, and their content is added to the output, such as the `output.urdf` file.

**Include Syntax**:

```yaml
include:
  path: /path/to/other.yaml
  variable1: value1
  variable2: value2
```

- **`path`**: The file path to the YAML file you want to include (required).
- **Additional Variables**: Pass variables to the included file by specifying them in the `include` block.

**Example Usage in the Model**:

```yaml
model:
  # Other model content
  include:
    path: /home/john/yamaro/leg.yaml
    leg_length: 1.0
    leg_radius: 0.05
  # Content from leg.yaml will be included here
```

**Accessing Returned Variables and Functions**:

Variables and functions defined in the included YAML file with scope `parent` or `global` become part of the current context. You can access them directly without a namespace.

---

### Control Structures

#### If Statements

Use `if` statements to conditionally execute sections of the code based on expressions. The `condition` is automatically evaluated, and you **do not** need to wrap the expression in `$()`.

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
  condition: arm_length > 1.0
  body:
    print: "Arm is long"
```

#### For Loops (Python-style `range`)

You can use `for` loops to iterate over ranges, similar to Python's `range()` function.

**Syntax**:

```yaml
for:
  iterator: variable_name
  range: start, stop, step  # 'step' is optional
  body:
    # Content to repeat
```

**Example**:

```yaml
for:
  iterator: i
  range: 5  # Just like Python's range(5)
  body:
    print: "Iteration $(i)"
```

---

### Printing and Process Statements

#### Printing

Use `print` to output messages during processing. Useful for debugging or providing information.

**Syntax**:

```yaml
print: message
```

**Example**:

```yaml
print: "Processing part: $(part_name)"
```

#### Process Statements

Use `process` to execute arbitrary Python code or evaluate expressions within your YAML file.

**Syntax**:

```yaml
process: expression
```

**Examples**:

```yaml
process: print("Current working directory:", os.getcwd())
process: my_variable = math.sqrt(16)
process: custom_function(variable_name)
```

---

### Custom XML Elements

You can define custom XML elements directly in your YAML file. Elements can have attributes and nested content.

**Syntax**:

```yaml
ElementName/attribute1=value1, attribute2=value2:
  # Nested content
```

**Example**:

```yaml
robot:
  link/name=my_link:
    inertial:
      mass/value=1.0:
      origin/xyz=0 0 0, rpy=0 0 0:
```

---

### Advanced Mathematical Expressions

Yamaro supports advanced mathematical expressions using Python syntax. Perform calculations within variable assignments or expressions using mathematical operators and functions.

**Example**:

```yaml
import:
  - math

variables:
  radius: 2.0
  area: $(math.pi * radius ** 2)
  circumference: $(2 * math.pi * radius)
print: "Circle with radius $(radius) has area $(area) and circumference $(circumference)"
```

---

### Custom Scopes and Variable Passing

Yamaro allows fine-grained control over variable scopes, including passing variables between included files and functions using different scopes:

- **`parent`**: Variables or functions with this scope are accessible in the parent context.
- **`child`**: Variables or functions are passed to child contexts (e.g., included files or called functions).
- **`bridge`**: Used to pass variables back and forth between included files and the main file.

**Example**:

```yaml
# In main.yaml
variables:
  shared_var/child: "This is shared with child"

model:
  include:
    path: child.yaml
    local_var: "Only in child"

# In child.yaml
variables:
  child_var/parent: "This comes from child"

print: "Accessing shared_var: $(shared_var)"
print: "Accessing local_var: $(local_var)"
```

---

### Command-Line Arguments

You can pass variables to the Yamaro script directly from the command line. These variables are immediately available in your YAML file.

**Usage**:

```bash
python3 yamaro.py input.yaml variable1:=value1 variable2:=value2
```

---

## Example: Building a Robot with Yamaro

**Main YAML File (`robot.yaml`)**:

```yaml
import:
  - math
  - os

variables:
  base_height/global: 0.5
  radius: 2.0

model:
  print: "Building robot with base height $(base_height)"
  process: print("Current working directory:", os.getcwd())

  # Base Part
  part:
    name: base
    link:
      geometry: cylinder
      scale: 0.3 $(base_height)
      mass: 5.0
      collision:
        geometry: cylinder
        scale: 0.3 $(base_height)
      visual:
        geometry: cylinder
        scale: 0.3 $(base_height)
        material:
          name: "Gray"
          color: 0.5 0.5 0.5 1
      inertial:
        mass: 5.0
    joint:
      type: fixed
      parent: root_link
      xyz: 0 0 0
      rpy: 0 0 0

  # Include the leg component within the model
  include:
    path: ./leg.yaml
    leg_length: 1.0
    leg_radius: 0.05

  # Build left leg with custom sensor code
  BuildLeg:
    side: left
    position: -0.15 0 0
    CustomCode:
      # Adding a sensor to the left leg using the Gazebo tag
      gazebo/reference='$(side)_leg_link':
        sensor/name='imu_sensor', type='imu':
          pose/degrees='true': 0 0 0 180 0 0
          always_on: 1
          update_rate: 1000

  # Build right leg without custom code
  BuildLeg:
    side: right
    position: 0.15 0 0

  process: print("Leg index from leg.yaml:", index)
```

**Included YAML File (`leg.yaml`)**:

```yaml
variables:
  index/global: 42

functions:
  BuildLeg/parent:
    input: side, position, **CustomCode
    body:
      # Build the leg part
      part:
        name: $(side)_leg
        joint:
          type: revolute
          parent: base
          xyz: $(position)
          rpy: 0 0 0
        link:
          geometry: cylinder
          scale: $(leg_radius) $(leg_length)
          mass: 2.0
          collision:
            geometry: cylinder
            scale: $(leg_radius) $(leg_length)
          visual:
            geometry: cylinder
            scale: $(leg_radius) $(leg_length)
            material:
              name: "Blue"
              color: 0 0 1 1
          inertial:
            mass: 2.0
      # Insert custom code if provided
      CustomCode:
        # Custom code will be inserted here
```

**Explanation**:

- **Function Definition**:
  - The `BuildLeg` function accepts parameters `side`, `position`, and `**CustomCode`.
  - It defines a leg with specified geometry and mass.
  - The `CustomCode:` block allows for optional custom code insertion.
- **Function Call with Custom Code**:
  - For the left leg, a sensor is added using the `gazebo` tag.
  - The sensor is attached to the `left_leg_link` and has specified properties.
- **No Custom Code for Right Leg**:
  - The right leg is built without a `CustomCode` block, so no sensor is added.

---

## Additional Notes

- **Include Command Placement**: The `include` command is used within the `model` section or function bodies, not at the root level.
- **Scopes**: Pay attention to variable and function scopes to control their accessibility and lifecycle.
- **Process Statements**: Within `process` statements, you **do not** need to use `$()` to wrap expressions.
- **If Statement Conditions**: In `if` statements, the `condition` is automatically evaluated; you **do not** need to use `$()`.

---

## Conclusion

Yamaro provides a powerful and flexible way to define robot models using YAML, with features like custom parts, loops, conditionals, and the ability to pass code snippets to functions using `**Block`. By accurately using the syntax and including elements like `collision`, `visual`, and `inertial` sections with the correct properties, you can create detailed and functional robot descriptions suitable for simulation and real-world applications.

---

## Getting Help

For more information, examples, or assistance, please refer to the project's GitHub repository or contact the maintainer.

---

## License

Yamaro is released under the GNU General Public License v3.0.

---

This README provides a detailed and accurate explanation of the Yamaro language, reflecting the code implementation. All syntax and usage examples have been carefully crafted to match the functionality of Yamaro, ensuring that users have a comprehensive and precise reference to effectively utilize the language.

---
