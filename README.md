# MeshmerizeMe
MeshmerizeMe is a set of Python scripts intended to convert image files into
geometry files for use with immersed boundary software like IBAMR and IB2D. 
It also includes the ability to plot the resulting .vertex files to verify 
the geometry looks as intended.

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

```
usage: ContourizeMe [-h] [--movie MOVIE] [--scale SCALE] image

allows the user to slide to a values for 8-bit pixel thresholding

positional arguments:
  image

optional arguments:
  -h, --help     show this help message and exit
  --movie MOVIE
  --scale SCALE
```

Call the `MeshmerizeMe` script to mesh the resulting SVG files.

```
usage: MeshmerizeMe [-h] [-i | -p] [fname [fname ...]]

Welcome to MeshmerizeMe. MeshmerizeMe is a Python script intended to assist
with creating geometries for fluid simulations using IBAMR and IB2d. It uses a
user-supplied SVG file and input2d file to create .vertex files, and can plot
the same.

positional arguments:
  fname             Path to file(s) for processing. If omitted, program will
                    run in batch-processing mode.

optional arguments:
  -h, --help        show this help message and exit
  -i, --input-file  Mesh SVG file(s). Default option. Exclusive with plot.
  -p, --plot        Plot existing .vertex file(s). Exclusive with input-file.

Note that the file argument is optional. If no file is specified on the
commandline the program will start in batch mode. If the user supplies the
path to one or more file(s) on the commandline, MeshmerizeMe will proceed to
process them.
```

# Installation
Use `pip install .` from the main package directory to install MeshmerizeMe.
If you prefer using a virtual environment with the supplied requirements.txt,
use

```shell
$ pip install . --no-deps
$ pip install -r requirements.txt  
```

## Requirements and Dependencies:

MeshmerizeMe was written for Python 3. Install requires are included in `setup.py`. A `requirements.txt` is also provided for user convenience. The minimal package requirements are: opencv, pandas, Pmw, scikit-image and scikit-learn, svgpathtools, and tqdm.
