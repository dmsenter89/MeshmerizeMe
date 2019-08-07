import sys, os
import argparse
#import MeshmerizeMe.uidesign as ui
import MeshmerizeMe.svg_parser as svg_parser
from MeshmerizeMe.input_parser import fetch_input_params
import MeshmerizeMe.geo_viewer as geo_viewer
from MeshmerizeMe.geo_obj import writeFile
import MeshmerizeMe.meshmerizeme_logger as logger


def batch(args):
    """
    Handles batch processing. Will iterate over stdin to process files.
    Takes into account whether the user wants to mesh or plot the files.
    """
    logger.info("MeshmerizeMe started in batch mode Will read from stdin.")
    for line in sys.stdin:
        path = line.strip()
        if path=='':
            break
        if args.input_file:
            mesh_file(path)
        elif args.plot:
            plot_file(path, display=False)
        else:
            logger.warning("You shouldn't see this line.")
    logger.info("Thank you for using MeshmerizeMe.")


def plot_file(fname, display=True):
    """
    Plots the file specified by fname. If display is set to False, the files
    will be saved to disk in the same folder the .vertex file was found in.
    This route is taken for batch processing. Otherwise, everything will be
    displayed.
    """
    fpath, v_name = os.path.split(fname)
    logger.info(("Processing {} for plotting.".format(v_name)))
    finput2d = os.path.join(fpath, 'input2d')
    params = fetch_input_params(finput2d)
    logger.info(("Successfully loaded simulation parameters from {}.".format(
                                finput2d)))
    vec = geo_viewer.read_vertices(fname)
    outputpath = fpath+params['string_name']+'.png'
    geo_viewer.plot_points(vec, params, display, path=outputpath)
    if display:
        logger.info(("Finished plotting {}.".format(v_name)))
    else:
        logger.info(("Plotted {} to {}.".format(v_name, outputpath)))


def mesh_file(fname):
    """
    Meshes file specified by fname.
    """
    fpath, svg_name = os.path.split(fname)
    logger.info(("Processing {} as SVG source file.".format(svg_name)))
    #all_paths, params = svg_parser.get_paths(args.svgfile)
    all_paths, params = svg_parser.get_paths(fname)
    logger.info(("Successfully extracted {} path(s) from the image.".format(
                                                        len(all_paths))))
    finput2d = os.path.join(fpath, 'input2d')
    params = fetch_input_params(finput2d, params)
    logger.info(("Successfully loaded simulation parameters from {}.".format(
                                finput2d)))
    vertices = svg_parser.make_vertices(all_paths, params)
    outFile = os.path.join(fpath, params['string_name'])
    writeFile(outFile, vertices)
    logger.info(("Vertices have been written to {}.vertex.".format(outFile)))


def process_all_files(args):
    """
    The main function for this program iterates over the given filenames
    and calls the appropriate functions on them, whether to mesh or plot
    the given experiment.
    """
    logger.info("MeshmerizeMe was started in CLI mode.")

    if args.input_file:
        logger.info("MeshmerizeMe was started in mesh-mode.")
        for f in args.fname:
            mesh_file(f.name)
        logger.info("MeshmerizeMe finished meshing your files. "
              "Please check your files for integrity.")
    elif args.plot:
        logger.info("MeshmerizeMe was started in plot mode.")
        for f in args.fname:
            plot_file(f.name)

    logger.info("Thank you for using MeshmerizeMe.")


# This main function is an "entry point" for the program as defined in
# setup.py . The function must not take any arguments, so we must
# read any command line arguments from sys.argv instead.
def main(args=None):
    if args is None:
        args = sys.argv[1:]

    parser = argparse.ArgumentParser(description = "Welcome to MeshmerizeMe. "
                "MeshmerizeMe is a Python script intended to assist with "
                "creating geometries for fluid simulations using IBAMR and "
                "IB2d. It uses a user-supplied SVG file and input2d file to "
                "create .vertex files, and can plot the same.",
                epilog = "Note that the file argument is optional. If no "
                "file is specified on the commandline the program will "
                "start in batch mode. If the user supplies the path to one or "
                "more file(s) on the commandline, MeshmerizeMe will proceed "
                "to process them.")
    arggroup = parser.add_mutually_exclusive_group()
    arggroup.add_argument('-i', '--input-file', action="store_true",
                        help="Mesh SVG file(s). Default option. "
                        "Exclusive with plot.",
                        default=True)
    arggroup.add_argument('-p', '--plot', action="store_true",
                help="Plot existing .vertex file(s). Exclusive with input-file.",
                default=False)
    parser.add_argument('fname', nargs='*', type=argparse.FileType('r'),
                help="Path to file(s) for processing. If omitted, program will "
                "run in batch-processing mode.")
    args = parser.parse_args()
    
    if args.plot:
            args.input_file=False
    if not args.fname:
        # assumes user wants to batch process files from stdi
        batch(args)
    else:
        # process the given files one by one
        process_all_files(args)