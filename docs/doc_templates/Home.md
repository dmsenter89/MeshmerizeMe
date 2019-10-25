Welcome to the MeshmerizeMe wiki!

# Summary 
MeshmerizeMe is a software for the creation of 2D geometry files for use with [IB2d](https://github.com/nickabattista/IB2d) and [IBAMR](https://github.com/IBAMR/IBAMR). The software comes with two main scripts that will be installed into your system's path:

- ContourizeMe: provides a graphical interface to automatically extract contours from an image into an SVG file based on adjustable parameters.
- MeshmerizeMe: creates *.vertex files describing the geometry of SVG images at the appropriate resolution according to an IB2d style `input2d` file. This script can also plot the resulting vertices for visual verification of their accuracy.

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
