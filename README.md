# MeshmerizeMe
MeshmerizeMe is a python script intended to convert SVG files into
geometry files for use with IBAMR and IB2D. This version will only
handle 2D code.

For the GUI we choose PyQt4. I have considered PyQt5 because it is newer and supported
by Qt, unlike PyQt4, but scientific windows users will most likely have installed
Python via Anaconda, which still bundles PyQt4 instead of v.5. TKinter was considered
but rejected.

## Input
SVG documents with 1:1 aspect ratio. Black lines will represent beams and black circles will be interpreted as masses.

## Output
File will write `ProjectName.OBJ` files, where `OBJ` will correspond to the geometry, such `vertex` or `spring`.

## Requirements:
Python 3.x. PyQt4.
