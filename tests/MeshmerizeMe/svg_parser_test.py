
import pytest
import os
import xml.etree.ElementTree as ET
from ...MeshmerizeMe import svg_parser


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
    assert False, "This test is unimplemented."



def test_Space___init__():
    assert False, "This test is unimplemented."

def test_Space_get_origin():
    assert False, "This test is unimplemented."

def test_Space_get_max_size():
    assert False, "This test is unimplemented."



def test_Svg___init__(SVG_TEST_STRUCTURES):   
    svg_file_structures = {}
    for file_name in SVG_TEST_STRUCTURES:
        svg_file_structures[file_name] = svg_parser.Svg( SVG_TEST_STRUCTURES[file_name]["absolute_file_path"] ) 

    for file_name in svg_file_structures:
        svg = svg_file_structures[file_name]
        assert svg.space is not None, "Should have a non-null 'space' property."
        assert svg.space.x == 0 and svg.space.y == 0, "Space should have an origin at (0,0)."
        assert svg.space.width == 300 and svg.space.height == 300, "Space should have a width and height of 300."
        assert svg.rattrib is not None, "Should have a non-null 'rattrib' property."    
        assert svg.objcts is not None and len(svg.objcts) > 1, "Should not have a null or empty 'objcts' property."
        assert svg.objcts[0].parent is None, "Root element should have a null parent property."
        assert svg.objcts[1].parent == svg.objcts[0], "Root element should be the parent of the second element in the 'objcts' property."

    assert len( svg_file_structures["box"].objcts ) == 2, "Should have 2 SVG element objects."
    assert len( svg_file_structures["box_paths"].objcts ) == 5, "Should have 5 SVG element objects."
    assert len( svg_file_structures["box_paths_grouped"].objcts ) == 6, "Should have 6 SVG element objects."
    assert len( svg_file_structures["box_paths_nested-grouped"].objcts ) == 9, "Should have 9 SVG element objects."
    assert len( svg_file_structures["box_paths_nested-grouped_translated"].objcts ) == 9, "Should have 9 SVG element objects."
    assert len( svg_file_structures["box_paths_nested-grouped_many-transforms"].objcts ) == 9, "Should have 9 SVG element objects."
    assert len( svg_file_structures["complex_shape"].objcts ) == 3, "Should have 3 SVG element objects."

def test_Svg_find_space():
    assert False, "This test is unimplemented."

def test_Svg_find_objects():
    assert False, "This test is unimplemented."

def test_Svg_get_paths():
    assert False, "This test is unimplemented."



def test_SvgObject___init__():
    assert False, "This test is unimplemented."

def test_SvgObject_get():
    assert False, "This test is unimplemented."

def test_SvgObject_print_object():
    assert False, "This test is unimplemented."

