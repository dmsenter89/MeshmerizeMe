#!/usr/bin/python
# -*- coding: utf-8 -*-

"""Python module to transform svg-paths into vertex files.

This file incorporates functions that will read in an svg file, parse it,
and transform this information into vertex points for use with IB2D and
IBAMR.

ISSUES:
    The SVG file needs to be in a very specific format for this to work.
    1) the file needs to have its height and width given in pixels, as simple
        float numbers, not in millimeters or anything, OR specify a viewBox.
    2) The svg *cannot* be using the translate feature or any other feature
        that alters its coordinate system relative to the viewbox.
    3) The svg parser cannot currently handle groups (<g> elements).
"""

import xml.etree.ElementTree as ET
from tqdm import tqdm
#from svg.path import parse_path
from svgpathtools import parse_path
from numpy import linspace
import numpy as np
from MeshmerizeMe.geo_obj import Vertex, writeFile
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
    mySvg = Svg(fname)
    paths = mySvg.get_paths()
    params['Space'] = mySvg.space
    w, h = params['Space'].get_max_size()
    params['width'] = w
    params['height'] = h
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
                sname = split_line[2]
                sname = sname.strip('"')
                print("sname={}".format(sname))
                params['SimName'] = sname
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
    # w = params['width']
    # h = params['height']
    w, h = params['Space'].get_max_size()
    x, y = params['Space'].get_origin()
    Lx = params['Lx']
    Ly = params['Ly']
    xnew = (z.real-x)*Lx/(w-x)
    ynew = (h-z.imag)*Ly/(h-y)
    return complex(xnew,ynew)


def points_on_path(path, params):
    """Figure out how many points are necessary and return those.

    Args:
        path: a path object.
        params: dictionary with parameters

    Returns:
        numpy array with the necessary number of evenly distributed points
        to dissect path objects at the necessary density.
    """
    #if method==1:
    #    length = path.length()  # lenght of path in svg system
    #    z = complex(length, params['height'])
    #    new_len = abs(coord_transform(z, params))
    #    num_of_pts = new_len//params['Ds']
    #    num_of_pts += 1
    #    point_array = linspace(0,1, num_of_pts)
    #else:
    # setup two temporary dummy points
    points = [0]
    p0 = 0
    p1 = 0
    ds = params['Ds']
    # keep track   of the ratio of 2nd to 1st deriv
    rato = np.abs(path.derivative(p0,2))/np.abs(path.derivative(p0,1))
    while p1<1:
        p1 = p0 + ds / np.abs(path.derivative(p0)) 
        if p1>1.01: # make sure we don't run outside of [0,1]
            break
        ratn = np.abs(path.derivative(p1,2))/np.abs(path.derivative(p1))
        if ratn/rato > 3: # large change in ratio, be careful
            try:
                # use previous two points as step instead
                p1 = p0 + (points[-1]-points[-2])
            except:
                # we don't have two steps available yet
                p1 = p0 + (1/3)*(p1-p0) # play with differnt vals
            ratn = np.abs(path.derivative(p1,2))/np.abs(path.derivative(p1))
        points.append(p1)
        p0 = p1
    point_array = np.asarray(points)
    return point_array


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
    print("Begin making vertices.")
    for path in tqdm(path_list):
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


class Space():
    """ Simple class representing a two-dimensional space.

    Class represents the two-dimensional space in which a path defined in an
    SVG lives. The class provides two getters returning tuples to get both the
    origin of the coordinate system as well as the max x/y values.

    Args:
        - boxstr: the string of the viewBox field in an SVG file.
    """
    def __init__(self, boxstr):
        boxvals = []
        for i in boxstr.split():
            boxvals.append(float(i))
        self.x = boxvals[0]
        self.y = boxvals[1]
        self.width = boxvals[2]
        self.height = boxvals[3]

    def get_origin(self):
        return (self.x, self.y)

    def get_max_size(self):
        return (self.width, self.height)


class Svg():
    """
    Class represents an SVG file with its paths and geometric objects.
    """

    def __init__(self, fname):
        """ Initializer takes file name (fname) and returns an object
        representing the objects in the Svg with their properties.
        """
        tree = ET.parse(fname)
        root = tree.getroot()
        self.rattrib = root.attrib
        self.space = self.find_space()
        self.objcts = self.find_objects(root)

    def find_space(self):
        """
        Class function that finds the space on which the elements in the
        SVG file are defined.
        """
        x,y,width,height = (0,0,-1,-1)  # default initialize, to be overwritten
        if 'viewBox' in self.rattrib:
            # easiest way to handles
            boxstr = self.rattrib['viewBox']
        else:
            if 'width' in self.rattrib:
                width = float(self.rattrib['width'])
            if 'height' in self.rattrib:
                height = float(self.rattrib['height'])

            # the following two checks are done to handle the fact that an SVG
            # space needs to only define the height or the width, with the other
            # assumed equal to the defined value
            if (width>0 and height<0):
                height = width
            if (width<0 and height>0):
                width = height

            # now create boxstr for Space class
            boxstr = "{} {} {} {}".format(x,y,width,height)

        mySpace = Space(boxstr)
        return mySpace

    def find_objects(self, rnode):
        """
        Quick function that generates a list of all path and other geometric
        objects in the SVG.
        """
        objs = [SvgObject(child) for child in rnode]
        return objs

    def get_paths(self):
        paths = []
        for elem in self.objcts:
            if elem.type=='path':
                paths.append(parse_path(elem.get('d')))
        return paths



class SvgObject():
    """
    Class to hold an object existing in an SVG. It includes functions to print
    an oject with its attribute dictionary as well as a generic getter to access
    the attributes from the internal dictionary.
    """

    def __init__(self, node):
        """
        initialize using a node returned by an ElementTree.
        """
        if '}' in node.tag:
            # this handles namespaces
            self.type = node.tag.split('}',1)[1]
        else:
            self.type = node.tag    # str holds name of object
        self.attr = node.attrib  # dic with attributes of element

    def get(self, attribute):
        """ Getter returns an attribute from the attribute dictionary as string.

        Args:
            - attribue: string representing the attribute searched for.

        Returns:
            String with the attribute value.
        """
        return self.attr[attribute]

    def print_object(self):
        """Print node name and attribute dictionary to console."""
        print("{} | {}".format(self.type, self.attr))


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
