# MeshmerizeMe
MeshmerizeMe is a set of Python scripts intended to convert image files into
geometry files for use with IBAMR and IB2D. Also includes the ability to
plot the resulting .vertex files to verify the geometry looks as intended.

This version will only handle 2D code. See the project wiki for more
information.

## Input and Output
- Input
    - An input2d file for the simulation.
    - An SVG file ___without___:
        - Nested viewBoxes/viewPorts
        - Nested `<svg>` elements
        - Use of the "preserveAspectRatio" attribute
        - Use of units other than pixels
        - `<use>`, `<symbol>`, and `<def>` tags
- Output
    - A .vertex file that can be plotted.

## Usage:
To convert image files into the intermediate SVG format, call the 
`ContourizeMe` script. It will start a GUI for extracting contours. 

To mesh the resulting SVG files, call the `MeshmerizeMe` script. 

```
MeshmerizeMe.py [-h] [--gui] [-i | -p] [fname [fname ...]]

Welcome to MeshmerizeMe. MeshmerizeMe is a Python script intended to assist
with creating geometries for fluid simulations using IBAMR and IB2d. It uses a
user-supplied SVG file and input2d file to create .vertex files, and can plot
the same.

positional arguments:
  fname             Path to file(s) for processing. If omitted, program will
                    run in batch-processing mode.

optional arguments:
  -h, --help        show this help message and exit
  --gui             Start GUI mode. Ignores other parameters.
  -i, --input-file  Mesh SVG file(s). Default option. Exclusive with plot.
  -p, --plot        Plot existing .vertex file(s). Exclusive with input-file.

Note that the file argument is optional. If no file is specified on the
commandline the program will start in batch mode. If the user supplies the
path to one or more file(s) on the commandline, MeshmerizeMe will proceed to
process them.
```

# Installation

See the wiki for installation instructions.

## Requirements and Dependencies:
Python 3.x. Matlab. NumPy. [tqdm](https://pypi.python.org/pypi/tqdm). [svg.path](https://pypi.python.org/pypi/svg.path). [OpenCV](https://pypi.org/project/opencv-python/).