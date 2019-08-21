#!/usr/bin/python
# -*- coding: utf-8 -*-

"""Python module to transform svg-paths into vertex files.

This file incorporates functions that will read in an svg file, parse it,
and transform this information into vertex points for use with IB2D and
IBAMR.

ISSUES:
    The SVG file needs to be in a very specific format for this to work.
    1) The file needs to have its height and width given in pixels as simple
        float numbers, not in millimeters or anything, OR specify a viewBox.
    2) The file can not contain:
        - Nested viewBoxes/viewPorts
        - Nested <svg> elements
        - Use of the "preserveAspectRatio" attribute
        - <use>, <symbol>, and <def> tags
"""

import xml.etree.ElementTree as ET
from tqdm import tqdm
from svgpathtools import parse_path
import svgpathtools
from numpy import linspace
import numpy as np
from .geo_obj import Vertex, writeFile
from . import meshmerizeme_logger as logger
import re
import warnings

ERROR_TOL = 0.10 # Error tolerance: 10% relative error

def get_paths(fname, params={}):
    """ Extract all paths and size from an svg file.

    This function scans over an svg to extract all paths as SvgObjects
    and extracts width and height of the svg file.

    Args:
        fname: filename/path to svg file of interest.
        params: python dictionary to hold the information about the svg.

    Returns:
        paths: a list of SvgObjects (svg_parser module).
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
                    if re.match(r"^\d+?(\.\d+)?$", s) is not None:
                        params['Lx'] = float(s)
            elif 'Ly' in line:
                for s in line.split():
                    if re.match(r"^\d+?(\.\d+)?$", s) is not None:
                        params['Ly'] = float(s)
            elif 'string_name' in line:
                split_line = line.split()
                sname = split_line[2]
                sname = sname.strip('"')
                logger.info(("sname={}".format(sname)))
                params['SimName'] = sname
    params['Ds'] = 0.5 * params['Lx'] / params['Nx']
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
    w, h = params['Space'].get_max_size()
    x, y = params['Space'].get_origin()
    Lx = params['Lx']
    Ly = params['Ly']
    xnew = (z.real - x) * Lx / (w - x)
    ynew = (h - z.imag) * Ly / (h - y)
    return complex(xnew, ynew)


def points_on_path(path, params):
    """Figure out how many points are necessary and return those.

    Args:
        path: a path object.
        params: dictionary with parameters

    Returns:
        numpy array with the necessary number of evenly distributed points
        to dissect path objects at the necessary density.
    """
    # setup two temporary dummy points
    points = [0]
    p0 = 0
    p1 = 0
    ds = params['Ds']
    # keep track   of the ratio of 2nd to 1st deriv
    rat0 = np.abs(path.derivative(p0, 2)) / np.abs(path.derivative(p0, 1))
    while p1<1:
        p1 = p0 + ds / np.abs(path.derivative(p0))
        if p1>1.0: # make sure we don't run outside of [0,1]
            break
        rat1 = np.abs(path.derivative(p1, 2)) / np.abs(path.derivative(p1))
        if rat0 != 0.0 and rat1/rat0 > 3: # large change in ratio, be careful
            try:
                # use previous two points as step instead
                p1 = p0 + (points[-1] - points[-2])
            except:
                # we don't have two steps available yet
                p1 = p0 + (1/3) * (p1 - p0) # play with differnt vals
            if p1>1.0: # make sure we don't run outside of [0,1]
                break
            rat1 = np.abs(path.derivative(p1, 2)) / np.abs(path.derivative(p1))
        points.append(p1)
        p0 = p1
        rat0 = rat1
    point_array = np.asarray(points)
    return point_array


def transform_matrix(params):
    xmax, ymax = params['Space'].get_max_size()
    xmin, ymin = params['Space'].get_origin()
    w = xmax-xmin
    h = ymax-ymin
    Lx = params['Lx']
    Ly = params['Ly']
    A = np.diag([Lx/w, Ly/h, 1])
    A[0,2] = -Lx*xmin/w
    A[1,2] = -Ly*ymin/h
    return A


def make_vertices(path_list, params):
    """Takes the paths and turns them into a list of vertex points.

    Args:
        path_list: python list containing path SvgObjects.
        params: dictionary containing all parameters.

    Returns:
        vertex_vec: list containing all vertex points obtained from the
        svg file.
    """
    vertex_vec = []
    error_vec = []
    warning_messages = []
    ds = params['Ds']
    logger.info("Begin making vertices.")

    A = transform_matrix(params) # Create point transform to target space

    for path in tqdm(path_list):
        path_as_svgpathtools_path = parse_path( path.get('d') )
        path_as_svgpathtools_path = transform( path_as_svgpathtools_path, path.get_aggregate_transform_matrix() )
        cur_point_index = 0

        for segment in path_as_svgpathtools_path:
            # Transform curves from SVG space -> experimental space
            ctrl_points_svg = np.asarray(segment.bpoints() )
            ctrl_points_svg_mat = np.ones((3, len(ctrl_points_svg) ))
            ctrl_points_svg_mat[0,:] = ctrl_points_svg.real
            ctrl_points_svg_mat[1,:] = ctrl_points_svg.imag
            ctrl_points_transformed_mat = np.matmul(A, ctrl_points_svg_mat)
            ctrl_points_transformed = ctrl_points_transformed_mat[0] + 1j* ctrl_points_transformed_mat[1]
            segment_transformed = svgpathtools.bpoints2bezier(ctrl_points_transformed)

            pts = points_on_path(segment_transformed, params)

    #        pts = points_on_path(path_as_svgpathtools_path, params)
            for p in pts:
                #print(f"Num of pts: {len(pts)}")
    #            z = path_as_svgpathtools_path.point(p)
                z = segment_transformed.point(p)
                #zn = coord_transform(z, params)
                cur_point = Vertex(z.real, z.imag)
                vertex_vec.append(cur_point)
                if cur_point_index > 0:
                    previous_point = vertex_vec[cur_point_index - 1]
                    distance = chk_vertex_dist(cur_point, previous_point)
                    rel_error = np.abs((distance - ds) / ds)
                    error_vec.append(rel_error)
                    if rel_error > ERROR_TOL:
                        warning_messages.append(f"Max Euclidean distance exceeded by {100*rel_error:.5f}% at vertex { cur_point.getPos() } on the path with attributes { path.attr }.")
                cur_point_index += 1

    for warning_message in warning_messages:
        logger.warning(warning_message)
    logger.info(f"Summary - Mean Rel. Err:  {100*np.mean(error_vec):.5f}%.")
    if len(warning_messages) > 0:
        logger.info("WARNING - Some points have spacing greater than the defined error tolerance. Please see the log file for details.")

    return vertex_vec


def chk_vertex_dist(a, b):
    """Helper function to check Euclidean distance between a and b.

    Args:
        a: Vertex object.
        b: Vertex object.

    Returns:
        Euclidean distance between vertex a and vertex b.
    """
    dx = a.x - b.x
    dy = a.y - b.y
    return (dx**2 + dy**2) ** (1/2)


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
        x, y, width, height = (0, 0, -1, -1)  # default initialize, to be overwritten
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
            boxstr = "{} {} {} {}".format(x, y, width, height)

        mySpace = Space(boxstr)
        return mySpace

    def find_objects(self, rnode):
        """
        Quick function that generates a list of all path and other geometric
        objects in the SVG.
        """
        objects = []
        element_tree_stack = []

        def push_element_and_its_parent_to_stack(element, parent):
            element_tree_stack.append( { "element" : element, "parent" : parent } )

        push_element_and_its_parent_to_stack(rnode, None)

        while len(element_tree_stack) > 0:
            curElementAndParent = element_tree_stack.pop()
            curElement = curElementAndParent["element"]
            parentOfCurElement = curElementAndParent["parent"]

            curElementAsSvgObject = SvgObject(curElement)
            curElementAsSvgObject.parent = parentOfCurElement
            objects.append(curElementAsSvgObject)

            for child_element in list(curElement):
                push_element_and_its_parent_to_stack(child_element, curElementAsSvgObject)

        return objects

    def get_paths(self):
        paths = []
        for elem in self.objcts:
            if elem.type=='path':
                paths.append(elem)
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
            self.type = node.tag.split('}', 1)[1]
        else:
            self.type = node.tag    # str holds name of object
        self.attr = node.attrib  # dic with attributes of element
        self.parent = None

    def __str__(self):
        return f"{self.type} | {self.attr}"

    def get(self, attribute):
        """ Getter returns an attribute from the attribute dictionary as string.

        Args:
            - attribue: string representing the attribute searched for.

        Returns:
            String with the attribute value.
        """
        return self.attr[attribute]

    def get_aggregate_transform_matrix(self):
        """
        Returns a matrix representing the aggregation of all transformations applied to this SvgObject.
        """
        transform_matrix = np.identity(3)
        cur_SvgObject = self
        while cur_SvgObject is not None:
            svg_transform_string = cur_SvgObject.get("transform") if "transform" in cur_SvgObject.attr else ""
            cur_transform_matrix = parse_transform(svg_transform_string)
            transform_matrix = np.dot(cur_transform_matrix, transform_matrix)
            cur_SvgObject = cur_SvgObject.parent
        return transform_matrix



# This function was taken as is from the svgpathtools library.
# https://github.com/mathandy/svgpathtools
# commit: 40a515ee63c1f2832628a84279e198fedd858c7e
def _check_num_parsed_values(values, allowed):
    if not any(num == len(values) for num in allowed):
        if len(allowed) > 1:
            warnings.warn('Expected one of the following number of values {0}, but found {1} values instead: {2}'
                          .format(allowed, len(values), values))
        elif allowed[0] != 1:
            warnings.warn('Expected {0} values, found {1}: {2}'.format(allowed[0], len(values), values))
        else:
            warnings.warn('Expected 1 value, found {0}: {1}'.format(len(values), values))
        return False
    return True


# This function was taken as is from the svgpathtools library.
# https://github.com/mathandy/svgpathtools
# commit: 40a515ee63c1f2832628a84279e198fedd858c7e
def _parse_transform_substr(transform_substr):

    type_str, value_str = transform_substr.split('(')
    value_str = value_str.replace(',', ' ')
    values = list(map(float, [_f for _f in value_str.split(' ') if _f]))

    transform = np.identity(3)
    if 'matrix' in type_str:
        if not _check_num_parsed_values(values, [6]):
            return transform

        transform[0:2, 0:3] = np.array([values[0:6:2], values[1:6:2]])

    elif 'translate' in transform_substr:
        if not _check_num_parsed_values(values, [1, 2]):
            return transform

        transform[0, 2] = values[0]
        if len(values) > 1:
            transform[1, 2] = values[1]

    elif 'scale' in transform_substr:
        if not _check_num_parsed_values(values, [1, 2]):
            return transform

        x_scale = values[0]
        y_scale = values[1] if (len(values) > 1) else x_scale
        transform[0, 0] = x_scale
        transform[1, 1] = y_scale

    elif 'rotate' in transform_substr:
        if not _check_num_parsed_values(values, [1, 3]):
            return transform

        angle = values[0] * np.pi / 180.0
        if len(values) == 3:
            offset = values[1:3]
        else:
            offset = (0, 0)
        tf_offset = np.identity(3)
        tf_offset[0:2, 2:3] = np.array([[offset[0]], [offset[1]]])
        tf_rotate = np.identity(3)
        tf_rotate[0:2, 0:2] = np.array([[np.cos(angle), -np.sin(angle)], [np.sin(angle), np.cos(angle)]])
        tf_offset_neg = np.identity(3)
        tf_offset_neg[0:2, 2:3] = np.array([[-offset[0]], [-offset[1]]])

        transform = tf_offset.dot(tf_rotate).dot(tf_offset_neg)

    elif 'skewX' in transform_substr:
        if not _check_num_parsed_values(values, [1]):
            return transform

        transform[0, 1] = np.tan(values[0] * np.pi / 180.0)

    elif 'skewY' in transform_substr:
        if not _check_num_parsed_values(values, [1]):
            return transform

        transform[1, 0] = np.tan(values[0] * np.pi / 180.0)
    else:
        # Return an identity matrix if the type of transform is unknown, and warn the user
        warnings.warn('Unknown SVG transform type: {0}'.format(type_str))

    return transform


# This function was taken as is from the svgpathtools library.
# https://github.com/mathandy/svgpathtools
# commit: 40a515ee63c1f2832628a84279e198fedd858c7e
def parse_transform(transform_str):
    """Converts a valid SVG transformation string into a 3x3 matrix.
    If the string is empty or null, this returns a 3x3 identity matrix"""
    if not transform_str:
        return np.identity(3)
    elif not isinstance(transform_str, str):
        raise TypeError('Must provide a string to parse')

    total_transform = np.identity(3)
    transform_substrs = transform_str.split(')')[:-1]  # Skip the last element, because it should be empty
    for substr in transform_substrs:
        total_transform = total_transform.dot(_parse_transform_substr(substr))

    return total_transform

# This function was taken (mostly) as is from the svgpathtools library.
# Minor adjustments were made so that the function can access the
# svgpathtools.path module.
# https://github.com/mathandy/svgpathtools
# commit: 40a515ee63c1f2832628a84279e198fedd858c7e
def transform(curve, tf):
    """Transforms the curve by the homogeneous transformation matrix tf"""
    def to_point(p):
        return np.array([[p.real], [p.imag], [1.0]])

    def to_vector(z):
        return np.array([[z.real], [z.imag], [0.0]])

    def to_complex(v):
        return v.item(0) + 1j * v.item(1)

    if isinstance(curve, svgpathtools.path.Path):
        return svgpathtools.path.Path(*[transform(segment, tf) for segment in curve])
    elif svgpathtools.path.is_bezier_segment(curve):
        return svgpathtools.path.bpoints2bezier([to_complex(tf.dot(to_point(p)))
                               for p in curve.bpoints()])
    elif isinstance(curve, svgpathtools.path.Arc):
        new_start = to_complex(tf.dot(to_point(curve.start)))
        new_end = to_complex(tf.dot(to_point(curve.end)))
        new_radius = to_complex(tf.dot(to_vector(curve.radius)))
        return svgpathtools.path.Arc(new_start, radius=new_radius, rotation=curve.rotation,
                   large_arc=curve.large_arc, sweep=curve.sweep, end=new_end)
    else:
        raise TypeError("Input `curve` should be a Path, Line, "
                        "QuadraticBezier, CubicBezier, or Arc object.")


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
