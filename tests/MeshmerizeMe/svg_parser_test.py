
import pytest
import os
import xml.etree.ElementTree as ET
import numpy as np
from ...MeshmerizeMe import svg_parser, geo_obj


SVG_TEST_FILES_DIRECTORY = os.path.join( os.path.dirname(__file__), "svg_test_files" )

@pytest.fixture
def SVG_TEST_STRUCTURES():
    svg_test_structures = {}
    for file_name in os.listdir(SVG_TEST_FILES_DIRECTORY):
        if ".svg" in file_name.lower():
            absolute_file_path = os.path.join(SVG_TEST_FILES_DIRECTORY, file_name )
            file_name = file_name.lower().replace(".svg","")
            svg_element_tree = ET.parse(absolute_file_path)
            svg_test_structures[file_name] = {
                "absolute_file_path" : absolute_file_path,
                "svg_element_tree" : svg_element_tree
            }
    return svg_test_structures

@pytest.fixture
def PARSED_SVG_TEST_STRUCTURES(SVG_TEST_STRUCTURES):
    parsed_svg_test_structures = {}
    for file_name in SVG_TEST_STRUCTURES:
        parsed_svg_test_structures[file_name] = svg_parser.Svg( SVG_TEST_STRUCTURES[file_name]["absolute_file_path"] ) 
    return parsed_svg_test_structures



def test_get_paths():
    assert False, "This test is unimplemented."

def test_get_sim_parameters():
    assert False, "This test is unimplemented."

def test_coord_transform():
    assert False, "This test is unimplemented."

def test_points_on_path():
    assert False, "This test is unimplemented."

def test_make_vertices():
    assert False, "This test is unimplemented."

def test_chk_vertex_dist():
    vertex1 = geo_obj.Vertex(-2,-1)
    vertex2 = geo_obj.Vertex(1,3)
    assert svg_parser.chk_vertex_dist(vertex1, vertex2) == 5, "Distance should be 5."
    assert svg_parser.chk_vertex_dist(vertex1, vertex1) == 0, "Distance should be 0."



def test_Space___init__():
    space = svg_parser.Space("30 40 500 700")
    assert space.x == 30, "X coordinate of origin should be 30."
    assert space.y == 40, "Y coordinate of origin should be 40."
    assert space.width == 500, "Width should be 500."
    assert space.height == 700, "Height should be 700."

def test_Space_get_origin():
    space = svg_parser.Space("30 40 500 700")
    origin = space.get_origin()
    assert origin[0] == 30 and origin[1] == 40, "Origin should be at (30,40)."

def test_Space_get_max_size():
    space = svg_parser.Space("30 40 500 700")
    max_size = space.get_max_size()
    assert max_size[0] == 500 and max_size[1] == 700, "Max size of space should be 500 x 700."


def test_Svg___init__(PARSED_SVG_TEST_STRUCTURES):   
    for file_name in PARSED_SVG_TEST_STRUCTURES:
        svg = PARSED_SVG_TEST_STRUCTURES[file_name]
        assert svg.space is not None, "Should have a non-null 'space' property."
        assert svg.rattrib is not None, "Should have a non-null 'rattrib' property."    
        assert svg.objcts is not None and len(svg.objcts) > 1, "Should not have a null or empty 'objcts' property."
    
def test_Svg_find_space(PARSED_SVG_TEST_STRUCTURES):
    for file_name in PARSED_SVG_TEST_STRUCTURES:
        svg = PARSED_SVG_TEST_STRUCTURES[file_name]
        assert svg.space is not None, "Should have a non-null 'space' property."
        assert svg.space.x == 0 and svg.space.y == 0, "Space should have an origin at (0,0)."
        assert svg.space.width == 300 and svg.space.height == 300, "Space should have a width and height of 300."

    svg = PARSED_SVG_TEST_STRUCTURES["box"]
    
    svg.rattrib = {"viewBox" : "100 100 200 300", "width" : "500", "height" : "700"}
    space = svg.find_space()
    assert space.x == 100 and space.y == 100 and space.width == 200 and space.height == 300, "Should use the space defined in the 'viewBox' attribute."

    svg.rattrib = {"width" : 500}
    space = svg.find_space()
    assert space.x == 0 and space.y == 0 and space.width == 500 and space.height == 500, "Should have the same width and height when only the width is specified."

    svg.rattrib = {"height" : 500}
    space = svg.find_space()
    assert space.x == 0 and space.y == 0 and space.width == 500 and space.height == 500, "Should have the same width and height when only the height is specified."

def test_Svg_find_objects(PARSED_SVG_TEST_STRUCTURES):
    for file_name in PARSED_SVG_TEST_STRUCTURES:
        svg = PARSED_SVG_TEST_STRUCTURES[file_name]   
        assert svg.objcts is not None and len(svg.objcts) > 1, "Should not have a null or empty 'objcts' property."
        assert svg.objcts[0].parent is None, "Root element should have a null parent property."
        assert svg.objcts[1].parent == svg.objcts[0], "Root element should be the parent of the second element in the 'objcts' property."

    assert len( PARSED_SVG_TEST_STRUCTURES["box"].objcts ) == 2, "Should have 2 SVG element objects."
    assert len( PARSED_SVG_TEST_STRUCTURES["box_paths"].objcts ) == 5, "Should have 5 SVG element objects."
    assert len( PARSED_SVG_TEST_STRUCTURES["box_paths_grouped"].objcts ) == 6, "Should have 6 SVG element objects."
    assert len( PARSED_SVG_TEST_STRUCTURES["box_paths_nested-grouped"].objcts ) == 9, "Should have 9 SVG element objects."
    assert len( PARSED_SVG_TEST_STRUCTURES["box_paths_nested-grouped_translated"].objcts ) == 9, "Should have 9 SVG element objects."
    assert len( PARSED_SVG_TEST_STRUCTURES["box_paths_nested-grouped_many-transforms"].objcts ) == 9, "Should have 9 SVG element objects."
    assert len( PARSED_SVG_TEST_STRUCTURES["complex_shape"].objcts ) == 3, "Should have 3 SVG element objects."

def test_Svg_get_paths(PARSED_SVG_TEST_STRUCTURES):
    paths = {}
    for file_name in PARSED_SVG_TEST_STRUCTURES:
        paths[file_name] = PARSED_SVG_TEST_STRUCTURES[file_name].get_paths()
    
    assert len( paths["box"] ) == 1, "Should have 1 path."
    assert len( paths["box"][0]._segments ) == 4, "First path should have 4 segments."
    assert len( paths["box_paths"] ) == 4, "Should have 4 paths."
    assert len( paths["box_paths"][0]._segments ) == 1, "First path should have 1 segment."   
    assert len( paths["box_paths_grouped"] ) == 4, "Should have 4 paths."
    assert len( paths["box_paths_grouped"][0]._segments ) == 1, "First path should have 1 segment."
    assert len( paths["box_paths_nested-grouped"] ) == 4, "Should have 4 paths."
    assert len( paths["box_paths_nested-grouped"][0]._segments ) == 1, "First path should have 1 segment."
    assert len( paths["box_paths_nested-grouped_translated"] ) == 4, "Should have 4 paths."
    assert len( paths["box_paths_nested-grouped_translated"][0]._segments ) == 1, "First path should have 1 segment."
    assert len( paths["box_paths_nested-grouped_many-transforms"] ) == 4, "Should have 4 paths."
    assert len( paths["box_paths_nested-grouped_many-transforms"][0]._segments ) == 1, "First path should have 1 segment."
    assert len( paths["complex_shape"] ) == 1, "Should have 1 path."
    assert len( paths["complex_shape"][0]._segments ) == 4, "First path should have 4 segments."



def test_SvgObject___init__(SVG_TEST_STRUCTURES):

    svg_element_tree_root_node = SVG_TEST_STRUCTURES["box"]["svg_element_tree"].getroot()
    first_child_of_root_node = list(svg_element_tree_root_node)[0] 
    svg_object1 = svg_parser.SvgObject( svg_element_tree_root_node )
    svg_object2 = svg_parser.SvgObject( first_child_of_root_node )
    assert svg_object1.type == "svg", "Should be a <svg> tag."
    assert svg_object1.attr is not None, "Should have a non-null attr property."
    assert svg_object1.attr["height"] == "300", "'height' attribute should be '300'."
    assert svg_object2.type == "path", "Should be a <path> tag."
    assert svg_object2.attr is not None, "Should have a non-null attr property."
    assert svg_object2.attr["stroke"] == "black" and svg_object2.attr["stroke-width"] == "3", "'stroke' attribute should be 'black', 'stroke-width' attribute should be '3'."

def test_SvgObject_get(SVG_TEST_STRUCTURES):
    svg_element_tree_root_node = SVG_TEST_STRUCTURES["box"]["svg_element_tree"].getroot()
    svg_object = svg_parser.SvgObject( svg_element_tree_root_node )
    assert svg_object.get("height") == "300", "Should return '300' for the 'height' attribute."

def test_SvgObject_get_aggregate_transform_matrix(PARSED_SVG_TEST_STRUCTURES):
    svg_objects = PARSED_SVG_TEST_STRUCTURES["box"].objcts
    path_svg_objects = [obj for obj in svg_objects if obj.type=="path"]
    assert np.array_equal( path_svg_objects[0].get_aggregate_transform_matrix(), np.identity(3) ), "Should not have any transformations."

    svg_objects = PARSED_SVG_TEST_STRUCTURES["box_paths_nested-grouped_many-transforms"].objcts
    path_svg_objects = [obj for obj in svg_objects if obj.type=="path"]
    
    expected_matrix_0 = np.array( [[ 6.123234e-16, -1.000000e+00,  2.500000e+02], [ 1.000000e+01,  6.123234e-17,  1.000000e+02], [ 0.000000e+00,  0.000000e+00,  1.000000e+00]] )
    expected_matrix_1 = np.array( [[ 6.123234e-16, -1.000000e+00,  2.000000e+01], [ 1.000000e+01,  6.123234e-17,  1.000000e+02], [ 0.000000e+00,  0.000000e+00,  1.000000e+00]] )
    expected_matrix_2 = np.array( [[ 23.,   0.,  20.], [  0.,   1., 200.], [  0.,   0.,   1.]] )
    expected_matrix_3 = np.array( [[ 23.,   0.,  20.], [  0.,   1., 100.], [  0.,   0.,   1.]] )

    assert np.allclose( path_svg_objects[0].get_aggregate_transform_matrix(), expected_matrix_0 ), "Should return a matrix representing all the transformations in the SVG file."
    assert np.allclose( path_svg_objects[1].get_aggregate_transform_matrix(), expected_matrix_1 ), "Should return a matrix representing all the transformations in the SVG file."
    assert np.allclose( path_svg_objects[2].get_aggregate_transform_matrix(), expected_matrix_2 ), "Should return a matrix representing all the transformations in the SVG file."
    assert np.allclose( path_svg_objects[3].get_aggregate_transform_matrix(), expected_matrix_3 ), "Should return a matrix representing all the transformations in the SVG file."


