# MeshmerizeMe
MeshmerizeMe is a python script intended to convert SVG files into
geometry files for use with IBAMR and IB2D. This version will only
handle 2D code.

See the project wiki for more information.

## Input
An SVG file with no grouping and an input2d file for the simulation.

## Output
A PROJECTNAME.vertex file ready for use with IB2d.

## Requirements:
Python 3.x. PyQt5. NumPy. [tqdm](https://pypi.python.org/pypi/tqdm). [svg.path](https://pypi.python.org/pypi/svg.path).
