#!/usr/bin/python
# -*- coding: utf-8 -*-

from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
import sys
import uidesign as ui
from svg_parser import *
from input_parser import fetch_input_params

class App(QMainWindow, ui.Ui_MainWindow):
    def __init__(self, parent=None):
        super(App, self).__init__(parent)
        self.setupUi(self)
        self.btnLoadFile.clicked.connect(self.load_file)
        self.actionOpen_File.triggered.connect(self.load_file)
        self.actionQuit.triggered.connect(self.close_app)
        self.actionAbout.triggered.connect(self.aboutDiag)

    def load_file(self):
        self.textEdit.clear()
        # request necessary files for svg_parser
        fname_svg = QFileDialog.getOpenFileName(self, "Open SVG File", '',
                                            "Vector Image(*.svg);;All Files (*)")
        fname_param = QFileDialog.getOpenFileName(self,
                                            "Open input2d File", '',
                                            "All Files (*)")
        self.textEdit.append('Loaded SVG and input2d files.')
        self.labTitle.setText('Thanks. Meshmerizing now.')
        all_paths, params = get_paths(fname_svg[0])
        self.textEdit.append('Successfully loaded {} path(s) '
                             'from image.'.format(len(all_paths)))
        #params = get_sim_parameters(fname_param[0], params)
        params = fetch_input_params(fname_param[0], params)
        self.textEdit.append('Loaded simulation parameters.')
        vertices = make_vertices(all_paths, params)
        self.textEdit.append('Vertices created.')
        outFile = params['string_name']
        writeFile(outFile, vertices)
        self.textEdit.append('Vertices written to {}.vertex'.format(outFile))
        self.textEdit.append('MeshmerizeMe completed. Please manually '
                            'verify your files for integrity.')

    def aboutDiag(self):
        text = "<h2>MeshmerizeMe 0.1</h2>"\
                "<p>Author: Michael Senter<br>UNC Chapel Hill, Miller Lab</p>"\
                "<p>MeshmerizeMe is a Python script intended to assist with "\
                "creating geometries for fluid simulations using IBAMR and "\
                "IB2d. It uses a user-supplied SVG file and input2d file "\
                "to create .vertex files."
        a = QMessageBox.about(self, "About", text)
        #a.exec_()

    def close_app(self):
        sys.exit()

def main():
    app = QApplication(sys.argv)
    form = App()
    form.show()
    app.exec_()

if __name__ == '__main__':
    main()
