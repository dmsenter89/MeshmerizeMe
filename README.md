This repository houses MeshmerizeMe, a software designed to help with the
creation of curvilinear meshes for use with IB2d and IBAMR. The repository is
organized into three folders:

- python: a prototype version of MeshmerizeMe in Python. It can handle SVG files
    that don't use groups and have a relatively simple structure. The full set
    of path attributes is implemented.
- cpp: a version of MeshmerizeMe written in C++. This folder is currently used
    mainly for testing purposes and does not (yet) represent fully functional
    code.
- test_files: simple SVG files for testing purposes, with a minimal input2d file
   included.

For more information on this project, see Michael Senter's website here.
