#!/usr/bin/env python3
# coding: utf-8

import matplotlib.pyplot as plt
#from PyQt5.QtGui import *
#from PyQt5.QWidget import *
#from geo_obj import *

def read_vertices(fname):
    """
    Function reads in supplied .vertex file and returns the vertex coordinates
    as a vector of complex numbers. These have the IB2d coordinate system, not
    the one ready to be plotted in PyQt.
    """
    vec = []
    f = open(fname, 'r')
    i = 0 # counter variable
    for line in f:
        if i>0:
            # do stuff
            parts = line.split()
            num = complex(float(parts[0]), float(parts[1]))
            vec.append(num)
        i += 1
    return vec

def plot_points(vec):
    """
    Plots vec as a scatter plot.
    """
    x = [elem.real for elem in vec]
    y = [elem.imag for elem in vec]
    plt.scatter(x, y)
    plt.show()
