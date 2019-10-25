# MeshmerizeMe
MeshmerizeMe is a set of Python scripts intended to convert image files into
geometry files for use with immersed boundary software like IBAMR and IB2D. 
It also includes the ability to plot the resulting .vertex files to verify 
the geometry looks as intended.

This version will only handle 2D code. See the project wiki for more
information.

## Usage:
To convert image files into the intermediate SVG format, call the 
`ContourizeMe` script. It will start a GUI for extracting contours. 

```
{{ render_params["contourizeme_help_message"] }}
```

Call the `MeshmerizeMe` script to mesh the resulting SVG files.

```
{{ render_params["meshmerizeme_help_message"] }}
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

# Limitations
{{ render_params["meshmerizeme_limitations"] }}