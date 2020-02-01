
import pytest
import os
import xml.etree.ElementTree as ET
import svgpathtools
import numpy as np
from MeshmerizeMe import svg_parser, points_estimation


SVG_TEST_FILES_DIRECTORY = os.path.join( os.path.dirname(__file__), "test_cases", "svg_test_files" )


@pytest.fixture
def PARSED_SVG_TEST_STRUCTURE():
    absolute_file_path = os.path.join(SVG_TEST_FILES_DIRECTORY, "box.svg")
    parsed_svg_test_structure = svg_parser.Svg(absolute_file_path) 
    return parsed_svg_test_structure

@pytest.fixture
def PARSED_SVG_TEST_STRUCTURE_PATHS(PARSED_SVG_TEST_STRUCTURE):
    absolute_file_path = os.path.join(SVG_TEST_FILES_DIRECTORY, "box.svg")
    paths_as_SvgObject, params = svg_parser.get_paths(absolute_file_path)
    paths_as_svgpathtools_path = [ svgpathtools.parse_path(path.get("d")) for path in paths_as_SvgObject ]
    return paths_as_svgpathtools_path

@pytest.fixture
def POINTS_ESTIMATION_USER_CONFIG(PARSED_SVG_TEST_STRUCTURE_PATHS):
    return {
        "path" : PARSED_SVG_TEST_STRUCTURE_PATHS[0],
        "ds" : 50,
        "min_T" : 0,
        "max_T" : 1,
        "point_params" : None,
        "subpath_length" : 25,
        "num_points" : None,
        "learning_rate" : 0.00005,
        "max_iter" : 50,
        "threshold" : 1e-6,
        "show_graph" : False,
        "num_parallel_processes" : 10
    }


def test_get_point_coords(PARSED_SVG_TEST_STRUCTURE_PATHS):
    path = PARSED_SVG_TEST_STRUCTURE_PATHS[0]
    point_params = [0.0, 0.2, 0.4, 0.6, 0.8, 1.0]
    expected_point_coords = np.asarray([ 20.0+100.0j, 152.0+100.0j, 250.0+134.0j, 184.0+200.0j,  52.0+200.0j, 20.0+100.0j ])
    actual_point_coords = points_estimation.get_point_coords(path, point_params)
    assert np.allclose(expected_point_coords, actual_point_coords), "Should return the correct 2D coordinates for each point parameter between 0 and 1."

    with pytest.raises(Exception):
        point_params = [-0.2]
        points_estimation.get_point_coords(path, point_params) # Should fail if point params are outside [0,1]

    with pytest.raises(Exception):
        point_params = [1.2]
        points_estimation.get_point_coords(path, point_params) # Should fail if point params are outside [0,1]

def test_get_segment_lengths():
    with pytest.raises(Exception):
        point_coords = None
        points_estimation.get_segment_lengths(point_coords) # Should fail with null point coords

    point_coords = [1, 2, np.nan, 3]
    assert np.nan not in points_estimation.get_segment_lengths(point_coords), "Result should not contain NaN values."

    point_coords = np.asarray([ [0,0], [1,1], [3,3], [6,6] ])
    expected_lengths = [1,2,3]
    actual_lengths = points_estimation.get_segment_lengths(point_coords)
    assert np.allclose(expected_lengths, actual_lengths), "Should return the correct segment lengths if inputs are valid."

def test_get_mean_squared_relative_error():
    segment_lengths = np.asarray([1, 2, np.nan, 3])
    expected_mse = 0.0
    actual_mse = points_estimation.get_mean_squared_relative_error(segment_lengths, 1)
    assert np.isclose(expected_mse, actual_mse), "Should ignore any NaN input values."

    segment_lengths = np.asarray([1,2,3,4])
    expected_mse = 0.0
    actual_mse = points_estimation.get_mean_squared_relative_error(segment_lengths, 1)
    assert np.isclose(expected_mse, actual_mse), "Should return the correct MSE if inputs are valid."

def test_GradientDescentEstimator___init__(POINTS_ESTIMATION_USER_CONFIG):
    estimator = points_estimation.GradientDescentEstimator(POINTS_ESTIMATION_USER_CONFIG)
    assert estimator.subpath_length == 1250, "Subpath length should be USER_CONFIG['subpath_length'] * USER_CONFIG['ds']."
    assert estimator.num_segments == 14, "num_segments should be ceil(path_length/ds)."
    assert estimator.num_points == 15, "num_points should be ceil(path_length/ds) + 1."
    assert np.allclose(estimator.point_params, np.linspace(0, 1, 15)), "Initial point params should be equally spaced."

def test_GradientDescentEstimator_get_mse_gradient(POINTS_ESTIMATION_USER_CONFIG):
    estimator = points_estimation.GradientDescentEstimator(POINTS_ESTIMATION_USER_CONFIG)
    expected_mse_gradient = np.asarray([ 8.16326531e-05,  0.00000000e+00,  0.00000000e+00,  0.00000000e+00, 1.49866919e-04,  4.97016776e-05,  0.00000000e+00, -8.16326531e-05, 0.00000000e+00, -8.12048841e-19, -1.62409768e-18,  1.49866919e-04, 4.97016776e-05, -1.62409768e-18, -8.16326531e-05 ])
    actual_mse_gradient = estimator.get_mse_gradient()
    assert np.allclose(expected_mse_gradient, actual_mse_gradient), "Should return the correct MSE gradient."

def test_GradientDescentEstimator_fit_subpath(POINTS_ESTIMATION_USER_CONFIG):
    estimator = points_estimation.GradientDescentEstimator(POINTS_ESTIMATION_USER_CONFIG)
    expected_point_params = np.asarray([ 0.0, 0.07142857, 0.14285714, 0.21428571, 0.28571428, 0.35714285, 0.42857143, 0.5, 0.57142857, 0.64285714, 0.71428571, 0.78571428, 0.85714285, 0.92857143, 1.0 ])
    actual_point_params = estimator.fit_subpath()
    assert np.allclose(expected_point_params, actual_point_params), "Should return correctly calculated point params."

def test_GradientDescentEstimator_fit_path(POINTS_ESTIMATION_USER_CONFIG):
    POINTS_ESTIMATION_USER_CONFIG["subpath_length"] = 5
    estimator = points_estimation.GradientDescentEstimator(POINTS_ESTIMATION_USER_CONFIG)
    expected_point_params = np.asarray([ 0.0, 0.07142857, 0.14285714, 0.21428571, 0.28571428, 0.35714285, 0.42857143, 0.5, 0.57142857, 0.64285714, 0.71428571, 0.78571428, 0.85714285, 0.92857143, 1.0 ])
    actual_point_params = estimator.fit_subpath()
    assert np.allclose(expected_point_params, actual_point_params), "Should return correctly calculated point params."
