#!/usr/bin/env python3
# coding: utf-8
import os
import argparse
import matplotlib.pyplot as plt
#from PyQt5.QtGui import *
#from PyQt5.QWidget import *
from svg_parser import get_sim_parameters

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

def plot_points(vec, params):
    """
    Plots vec as a scatter plot.
    """
    x = [elem.real for elem in vec]
    y = [elem.imag for elem in vec]
    plt.scatter(x, y, s=2)
    title_string = params['SimName'] + ' Experiment'
    plt.title(title_string)
    plt.xlabel('Width in meters')
    plt.ylabel('Height in meters')
    plt.axis([0, params['Lx']*1.1, 0, params['Ly']*1.1])
    plt.grid(True)
    plt.show()

def main(infilepath):
    path, infile = os.path.split(infilepath)
    print('Got the file and path, getting started.')
    params = {}
    params = get_sim_parameters(infilepath, params)
    svgfile = path + params['SimName'] + '.vertex'
    vec = read_vertices(path + params['SimName'] + '.vertex')
    plot_points(vec, params)
    print('File Plotted. Thank you.')

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description = 'Script to visualize a '
                                    '.vertex file in matplotlib.')
    parser.add_argument('-p', '--param', required=True,
                        help='Path to input2d for sim')
    args = parser.parse_args()
    if args.param:
        main(args.param)
    else:
        print('GUI version not implemented yet. Use terminal. See -h.')
