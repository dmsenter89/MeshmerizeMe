"""
MMeSolveSVC
-----------

Description:
Solves an SVC with sklearn according to this guide:
http://www.csie.ntu.edu.tw/~cjlin/papers/guide/guide.pdf

The SVC is determined by default with a RBF (Radial Basis Function) and thus
has two parameters to choose (C and gamma).  The script search a log-2
2d (C, gamma) grid of coordinates and chooses the best fit bases on a
cross-validated test of the model performed by randomly choosing training and
test samples from the supplied points.

It outputs a pickled GridSearchCV object that contains the fitted classifier and
can be used to predict binary images with the script MMePredictBinaryImage.

Example:

MMeSolveSVC samples_v1.pkl --verbose --ofile svc_v1.pkl

Args:
    ifile: the path of the output pickle of MMeSamplePixels which includes a
           filename or list of filenames of images and a dictionary containing
           foreground and background pixel locations in those images.
    --ofile: the path of the pickle write the solved classifier to
    --verbose: whether to display logging messages and the progress of the solver
    --n_passes: how many passes of the grid search algorithm to run.  Makes a finer and finer
                each time, where the new grid is centered on the previous maximum found.

"""

import numpy as np
import argparse as ap
import logging
import pickle
import cv2
import sys

from sklearn.model_selection import GridSearchCV
from sklearn import svm

# This main function is an "entry point" for the program as defined in
# setup.py . The function must not take any arguments, so we must
# read any command line arguments from sys.argv instead.
def main(args=None):
    if args is None:
        args = sys.argv[1:]

    parser = ap.ArgumentParser()
    parser.add_argument("ifile", default = "None")
    parser.add_argument("--ofile", default = "svc.pkl")
    parser.add_argument("--verbose", action = "store_true")
    parser.add_argument("--n_passes", default = "1")

    args = parser.parse_args()

    # set the verbosity
    if args.verbose:
        logging.basicConfig(level=logging.DEBUG)
        logging.debug("running in verbose mode")
    else:
        logging.basicConfig(level=logging.INFO)

    # read the filename and the sample pixel coordinates
    image, points = pickle.load(open(args.ifile))

    # the window size of the sample to use
    window_size = 0

    # read the image
    image = cv2.imread(image)

    # lists to contain the N-dimensional samples to solve upon
    X = []
    Y = []

    # get the foreground points
    fg = points['Foreground']

    nz = list(set(fg.nonzero()[0]))

    for ix in nz:
        
        x, y = list(map(int, list(fg[ix].toarray()[0])))
        
        y = image.shape[0] - y

        x = image[y - window_size:y + window_size + 1, x - window_size:x + window_size + 1].flatten().astype(np.float32)
        if len(x) != 0:

            X.append(x)
            
            Y.append(1.)

    # get the background points
    bg = points['Background']

    nz = list(set(bg.nonzero()[0]))

    for ix in nz:
        x, y = list(map(int, list(bg[ix].toarray()[0])))
        y = image.shape[0] - y

        x = image[y - window_size:y + window_size + 1, x - window_size:x + window_size + 1].flatten().astype(np.float32)

        if len(x) != 0:

            X.append(x)
            Y.append(0.)


    # convert to array to solve
    X = np.array(X)
    Y = np.array(Y)

    # the initial grid
    # Use the log-2 grid given as an example in the guide
    gamma = np.power(2., list(range(-15, 4)))
    C = np.power(2., list(range(-5, 16)))
    
    # for an RBF (radial basis function) kernel function
    parameters = {'kernel':['rbf'], 'C': C, 'gamma': gamma, 'class_weight': ['balanced']}
    
    svr = svm.SVC()
    clf = GridSearchCV(svr, parameters, verbose = 2)

    clf.fit(X, Y)

    # write the file
    pickle.dump(clf, open(args.ofile, 'w'))
    logging.debug('root: wrote the SVC to {0}'.format(args.ofile))

    

    

    

    
    

