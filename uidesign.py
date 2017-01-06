# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'uidesign.ui'
#
# Created by: PyQt5 UI code generator 5.7
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(412, 320)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.centralwidget)
        self.verticalLayout.setObjectName("verticalLayout")
        self.labTitle = QtWidgets.QLabel(self.centralwidget)
        self.labTitle.setObjectName("labTitle")
        self.verticalLayout.addWidget(self.labTitle)
        self.textEdit = QtWidgets.QTextEdit(self.centralwidget)
        self.textEdit.setObjectName("textEdit")
        self.verticalLayout.addWidget(self.textEdit)
        self.btnLoadFile = QtWidgets.QPushButton(self.centralwidget)
        self.btnLoadFile.setObjectName("btnLoadFile")
        self.verticalLayout.addWidget(self.btnLoadFile)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 412, 25))
        self.menubar.setObjectName("menubar")
        self.menuFile = QtWidgets.QMenu(self.menubar)
        self.menuFile.setObjectName("menuFile")
        self.menuHelp = QtWidgets.QMenu(self.menubar)
        self.menuHelp.setObjectName("menuHelp")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)
        self.actionQuit = QtWidgets.QAction(MainWindow)
        self.actionQuit.setObjectName("actionQuit")
        self.actionOpen_File = QtWidgets.QAction(MainWindow)
        self.actionOpen_File.setObjectName("actionOpen_File")
        self.actionAbout = QtWidgets.QAction(MainWindow)
        self.actionAbout.setObjectName("actionAbout")
        self.actionView_Geometry = QtWidgets.QAction(MainWindow)
        self.actionView_Geometry.setObjectName("actionView_Geometry")
        self.menuFile.addAction(self.actionOpen_File)
        self.menuFile.addAction(self.actionView_Geometry)
        self.menuFile.addSeparator()
        self.menuFile.addAction(self.actionQuit)
        self.menuHelp.addAction(self.actionAbout)
        self.menubar.addAction(self.menuFile.menuAction())
        self.menubar.addAction(self.menuHelp.menuAction())

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MeshmerizeMe"))
        self.labTitle.setText(_translate("MainWindow", "Welcome to MeshmerizeMe!\n"
"Please select a file to continue."))
        self.btnLoadFile.setText(_translate("MainWindow", "Load SVG"))
        self.menuFile.setTitle(_translate("MainWindow", "File"))
        self.menuHelp.setTitle(_translate("MainWindow", "Help"))
        self.actionQuit.setText(_translate("MainWindow", "Quit"))
        self.actionOpen_File.setText(_translate("MainWindow", "Load SVG"))
        self.actionAbout.setText(_translate("MainWindow", "About MeshmerizeMe"))
        self.actionView_Geometry.setText(_translate("MainWindow", "View Geometry (Lag Pts)"))

