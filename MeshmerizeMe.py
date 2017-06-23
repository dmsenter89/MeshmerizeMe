#!/usr/bin/python
# -*- coding: utf-8 -*-

from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
import sys, os
import argparse
import uidesign as ui
import svg_parser
from input_parser import fetch_input_params
import geo_viewer
from geo_obj import writeFile

class App(QMainWindow, ui.Ui_MainWindow):
    def __init__(self, parent=None):
        super(App, self).__init__(parent)
        self.setupUi(self)
        self.btnLoadFile.clicked.connect(self.load_file)
        self.actionOpen_File.triggered.connect(self.load_file)
        self.actionQuit.triggered.connect(self.close_app)
        self.actionAbout.triggered.connect(self.aboutDiag)
        self.actionView_Geometry.triggered.connect(self.geoView)

    def load_file(self):
        self.textEdit.clear()
        # request necessary files for svg_parser
        fname_svg = QFileDialog.getOpenFileName(self, "Open SVG File", '',
                                            "Vector Image(*.svg);;All Files (*)")
        fpath, svg_name = os.path.split(fname_svg[0])
        self.textEdit.append('Loaded SVG and input2d files.')
        self.labTitle.setText('Thanks. Meshmerizing now.')
        all_paths, params = svg_parser.get_paths(fname_svg[0])
        self.textEdit.append('Successfully loaded {} path(s) '
                             'from image.'.format(len(all_paths)))
        finput2d = os.path.join(fpath, 'input2d')
        params = fetch_input_params(finput2d, params)
        self.textEdit.append('Loaded simulation parameters '
                            'from {}.'.format(finput2d))
        vertices = svg_parser.make_vertices(all_paths, params)
        self.textEdit.append('Vertices created.')
        outFile = os.path.join(fpath,params['string_name'])
        writeFile(outFile, vertices)
        self.textEdit.append('Vertices written to {}.vertex'.format(outFile))
        self.textEdit.append('MeshmerizeMe completed. Please manually '
                            'verify your files for integrity.')

    def geoView(self):
        fnamepath = QFileDialog.getOpenFileName(self,
                                                "Open input2d File", '',
                                                "All Files (*)")
        path, infile = os.path.split(fnamepath[0])
        self.textEdit.setText("Opened {}.".format(fnamepath[0]))
        finput2d = os.path.join(path,'input2d')
        self.textEdit.append("Begin processing parameters "
                            "from {}.".format(finput2d))
        params = fetch_input_params(finput2d)
        vec = geo_viewer.read_vertices(fnamepath[0])
        geo_viewer.plot_points(vec, params)
        self.textEdit.append("Plotting completed.")

    def aboutDiag(self):
        text = "<h2>MeshmerizeMe 0.1</h2>"\
                "<p>Author: Michael Senter<br>UNC Chapel Hill, Miller Lab</p>"\
                "<p>MeshmerizeMe is a Python script intended to assist with "\
                "creating geometries for fluid simulations using IBAMR and "\
                "IB2d. It uses a user-supplied SVG file and input2d file "\
                "to create .vertex files."
        a = QMessageBox.about(self, "About", text)

    def close_app(self):
        sys.exit()

def mainGUI():
    app = QApplication(sys.argv)
    form = App()
    form.show()
    app.exec_()

def batch(args):
    """
    Handles batch processing. Will iterate over stdin to process files.
    Takes into account whether the user wants to mesh or plot the files.
    """
    print("MeshmerizeMe started in batch mode Will read from stdin.")
    for line in sys.stdin:
        path = line.strip()
        if path=='':
            break
        if args.input_file:
            mesh_file(path)
        elif args.plot:
            plot_file(path, display=False)
        else:
            print("You shouldn't see this line.")
    print("\nThank you for using MeshmerizeMe.")


def plot_file(fname, display=True):
    """
    Plots the file specified by fname. If display is set to False, the files
    will be saved to disk in the same folder the .vertex file was found in.
    This route is taken for batch processing. Otherwise, everything will be
    displayed.
    """
    fpath, v_name = os.path.split(fname)
    print("\nProcessing {} for plotting.".format(v_name))
    finput2d = os.path.join(fpath, 'input2d')
    params = fetch_input_params(finput2d)
    print("Successfully loaded simulation parameters from {}.".format(
                                finput2d))
    vec = geo_viewer.read_vertices(fname)
    outputpath = fpath+params['string_name']+'.png'
    geo_viewer.plot_points(vec, params, display, path=outputpath)
    if display:
        print("Finished plotting {}.".format(v_name))
    else:
        print("Plotted {} to {}.".format(v_name, outputpath))


def mesh_file(fname):
    """
    Meshes file specified by fname.
    """
    fpath, svg_name = os.path.split(fname)
    print("\nProcessing {} as SVG source file.".format(svg_name))
    #all_paths, params = svg_parser.get_paths(args.svgfile)
    all_paths, params = svg_parser.get_paths(fname)
    print("Successfully extracted {} path(s) from the image.".format(
                                                        len(all_paths)))
    finput2d = os.path.join(fpath, 'input2d')
    params = fetch_input_params(finput2d, params)
    print("Successfully loaded simulation parameters from {}.".format(
                                finput2d))
    vertices = svg_parser.make_vertices(all_paths, params)
    outFile = os.path.join(fpath,params['string_name'])
    writeFile(outFile, vertices)
    print("Vertices have been written to {}.vertex.".format(outFile))


def main(args):
    """
    The main function for this program iterates over the given filenames
    and calls the appropriate functions on them, whether to mesh or plot
    the given experiment.
    """
    print("MeshmerizeMe was started in CLI mode.")

    if args.input_file:
        print("MeshmerizeMe was started in mesh-mode.")
        for f in args.fname:
            mesh_file(f.name)
        print("\nMeshmerizeMe finished meshing your files."
              "Please check your files for integrity.")
    elif args.plot:
        print("MeshmerizeMe was started in plot mode.")
        for f in args.fname:
            plot_file(f.name)

    print("\nThank you for using MeshmerizeMe.")


if __name__ == '__main__':
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
    parser.add_argument('--gui', action="store_true", help="Start GUI mode. "
                        "Ignores other parameters.")
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
    if args.gui:    # start GUI if that's what user wants
        mainGUI()
    else:
        if args.plot:
                args.input_file=False
        if not args.fname:
            # assumes user wants to batch process files from stdi
            batch(args)
        else:
            # process the given files one by one
            main(args)
