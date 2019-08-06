import numpy as np
import argparse as ap
import logging
import pickle
import cv2
import sys

# This main function is an "entry point" for the program as defined in
# setup.py . The function must not take any arguments, so we must
# read any command line arguments from sys.argv instead.
def main(args=None):
    if args is None:
        args = sys.argv[1:]

    parser = ap.ArgumentParser()
    parser.add_argument("ifile", default = "None")
    parser.add_argument("--svm", default = "None")
    parser.add_argument("--ofile", default = "None")

    args = parser.parse_args()

    

    
