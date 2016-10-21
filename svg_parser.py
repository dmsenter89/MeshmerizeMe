#!/usr/bin/python
# -*- coding: utf-8 -*-

"""Python module to transform svg-paths into vertex files.

This file incorporates functions that will read in an svg file, parse it,
and transform this information into vertex points for use with IB2D and
IBAMR.

ISSUES:
    The SVG file needs to be in a very specific format for this to work.
    1) the file needs to have it's height and width given in pixels, as simple
        float numbers, not in millimeters or anything.
    2) The svg *cannot* be using the translate feature or any other feature
        that alters its coordinate system relative to the viewbox.
"""

from xml.dom import minidom
from svg.path import parse_path
from numpy import linspace
from geo_obj import Vertex, writeFile
import re


def get_paths(fname, params={}):
    """ Extract all paths and size from an svg file.

    This function scans over an svg to extract all paths as svg.path path objects
    and extracts width and height of the svg file.

    Args:
        fname: filename/path to svg file of interest.
        params: python dictionary to hold the information about the svg.

    Returns:
        paths: a list of path objects (svg.path module).
        params: dictionary updated with the extracted information.
    """
    svg_doc = minidom.parse(fname)
    path_strings = [path.getAttribute('d') for path in svg_doc.getElementsByTagName('path')]
    for info in svg_doc.getElementsByTagName('svg'):
        params['width'] = float(info.getAttribute('width'))
        params['height'] = float(info.getAttribute('height'))
    svg_doc.unlink()
    paths = [parse_path(p) for p in path_strings]
    return paths, params


def get_sim_parameters(fname, params):
    """
    Function that extracts parameters from an 'input2d' file.

    Args:
        fname:  filename/path to 'input2d' file.
        params: python dictionary to hold the information.

    Returns:
        params: dictionary updated with extracted information.
    """
    with open(fname, 'r') as inFile:
        for line in inFile:
            if 'Nx' in line:
                for s in line.split():
                    if s.isdigit():
                        params['Nx'] = int(s)
            elif 'Ny' in line:
                for s in line.split():
                    if s.isdigit():
                        params['Ny'] = int(s)
            elif 'Lx' in line:
                for s in line.split():
                    if re.match("^\d+?(\.\d+)?$", s) is not None:
                        params['Lx'] = float(s)
            elif 'Ly' in line:
                for s in line.split():
                    if re.match("^\d+?(\.\d+)?$", s) is not None:
                        params['Ly'] = float(s)
            elif 'string_name' in line:
                split_line = line.split()
                params['SimName'] = split_line[2]
    params['Ds'] = 0.5*params['Lx']/params['Nx']
    return params


def coord_transform(z, params):
    """Transform the coordinates from SVG to input2d ready coordinates.

    This function takes a point z in [0,width]x[0,height] to a point
    z in [0,Lx]x[0,Ly] using a linear transform.

    Args:
        z: complex number representing a point in the svg.
        params: dictionary with parameters.

    Returns:
        complex(x,y): complex number representing point in input2d coordinates.
    """
    w = params['width']
    h = params['height']
    Lx = params['Lx']
    Ly = params['Ly']
    x = z.real*Lx/w
    y = (h-z.imag)*Ly/h
    return complex(x,y)


def points_on_path(path, params):
    """Figure out how many points are necessary and return those.

    Args:
        path: a path object.
        params: dictionary with parameters

    Returns:
        numpy array with the necessary number of evenly distributed points
        to dissect path objects at the necessary density.
    """
    length = path.length()  # lenght of path in svg system
    z = complex(length, params['height'])
    new_len = abs(coord_transform(z, params))
    num_of_pts = new_len//params['Ds']
    num_of_pts += 1
    return linspace(0,1, num_of_pts)


def make_vertices(path_list, params):
    """Takes the paths and turns them into a list of vertex points.

    Args:
        path_list: python list containing path objects.
        params: dictionary containing all parameters.

    Returns:
        vertex_vec: list containing all vertex points obtained from the
        svg file.
    """
    vertex_vec = []
    for path in path_list:
        cvert_vec = []
        pts = points_on_path(path,params)
        for p in pts:
            z = path.point(p)
            zn = coord_transform(z,params)
            vpoint = Vertex(zn.real, zn.imag)
            cvert_vec.append(vpoint)
        vertex_vec.extend(cvert_vec)
    return vertex_vec


def chk_vertex_dist(a,b):
    """Helper function to check Euclidean distance between a and b.

    Args:
        a: Vertex object.
        b: Vertex object.

    Returns:
        Euclidean distance between vertex a and vertex b.
    """
    dx = a.x-b.x
    dy = a.y-b.y
    return (dx**2+dy**2)**(1/2)


def test():
    """Function that demonstrates the abilities of the module."""
    print('Run script test')
    print('Reading in sample paths from "simple.svg."')
    params = {}   # initialize empty parameter dictionary
    all_paths, params = get_paths('simple.svg', params)
    print('Reading in parameters from "input2d".')
    params = get_sim_parameters('input2d', params)
    print('Making the vertices.')
    vertices = make_vertices(all_paths, params)
    print('Writing "test.vertex".')
    writeFile('test', vertices)
    print('Finished demo.')

if __name__ == '__main__': test()
