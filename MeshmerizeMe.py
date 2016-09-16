# -*- coding: utf-8 -*-
from PyQt4.QtGui import *
import sys
import uidesign as ui

class App(QMainWindow, ui.Ui_MainWindow):
    def __init__(self, parent=None):
        super(App, self).__init__(parent)
        self.setupUi(self)
        self.btnLoadFile.clicked.connect(self.load_file)
        self.actionQuit.triggered.connect(self.close_app)

    def load_file(self):
        self.textEdit.clear()
        fname = QFileDialog.getOpenFileName(self, "Open SVG File", '', "Vector Image(*.svg);;All Files (*)")
        if fname:
            ftext=open(fname).read()
            self.textEdit.setPlainText(ftext)

    def close_app(self):
        sys.exit()

def main():
    app = QApplication(sys.argv)
    form = App()
    form.show()
    app.exec_()

if __name__ == '__main__':
    main()
