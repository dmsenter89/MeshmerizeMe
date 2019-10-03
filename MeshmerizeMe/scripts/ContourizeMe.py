"""
ContourizeMe

Description:
A Tkinter GUI for creating SVGs from manually finding contours in an image.  The user manually selects lower and upper bounds in a given
paramaterization of pixel space (Grayscale, RGB, HSV).

"""

from MeshmerizeMe import get_diameters, Chanvese, Contours
import MeshmerizeMe.meshmerizeme_logger as logger


try: # for Py3
    from tkinter import *
except: # legacy Py2 support
    from tkinter import *
    import tkinter.filedialog
import pickle
import cv2
import numpy as np
import logging
import argparse
from PIL import ImageTk, Image
import sys
import copy
from skimage.io import imread
from scipy.interpolate import insert
from numpy import asarray, unique, split, sum
from scipy import interpolate
from svgpathtools import CubicBezier, wsvg
from scipy.spatial import KDTree
import pandas as pd
from scipy.interpolate import UnivariateSpline
from MeshmerizeMe import get_diameters, Chanvese, Contours
from MeshmerizeMe.tools import *

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.backend_bases import MouseEvent
from matplotlib.figure import Figure

from scipy.stats import norm
import scipy.ndimage as nd

import numpy as np
import scipy.ndimage as nd
import matplotlib.pyplot as plt

import Pmw
import skimage
import os

eps = np.finfo(float).eps


def map_uint16_to_uint8(img, lower_bound=None, upper_bound=None):
    '''
    Map a 16-bit image trough a lookup table to convert it to 8-bit.

    Parameters
    ----------
    img: numpy.ndarray[np.uint16]
        image that should be mapped
    lower_bound: int, optional
        lower bound of the range that should be mapped to ``[0, 255]``,
        value must be in the range ``[0, 65535]`` and smaller than `upper_bound`
        (defaults to ``numpy.min(img)``)
    upper_bound: int, optional
       upper bound of the range that should be mapped to ``[0, 255]``,
       value must be in the range ``[0, 65535]`` and larger than `lower_bound`
       (defaults to ``numpy.max(img)``)

    Returns
    -------
    numpy.ndarray[uint8]
    '''
    if not(0 <= lower_bound < 2**16) and lower_bound is not None:
        raise ValueError(
            '"lower_bound" must be in the range [0, 65535]')
    if not(0 <= upper_bound < 2**16) and upper_bound is not None:
        raise ValueError(
            '"upper_bound" must be in the range [0, 65535]')
    if lower_bound is None:
        lower_bound = np.min(img)
    if upper_bound is None:
        upper_bound = np.max(img)
    if lower_bound >= upper_bound:
        raise ValueError(
            '"lower_bound" must be smaller than "upper_bound"')
    lut = np.concatenate([
        np.zeros(lower_bound, dtype=np.uint16),
        np.linspace(0, 255, upper_bound - lower_bound).astype(np.uint16),
        np.ones(2**16 - upper_bound, dtype=np.uint16) * 255
    ])
    return lut[img].astype(np.uint8)

contours = None
imgray = None

from scipy.optimize import minimize
from scipy.spatial.distance import euclidean
import random

class AutoScrollbar(Scrollbar):
    ''' A scrollbar that hides itself if it's not needed.
        Works only if you use the grid geometry manager '''
    def set(self, lo, hi):
        if float(lo) <= 0.0 and float(hi) >= 1.0:
            self.grid_remove()
        else:
            self.grid()
            Scrollbar.set(self, lo, hi)

    def pack(self, **kw):
        raise TclError('Cannot use pack with this widget')

    def place(self, **kw):
        raise TclError('Cannot use place with this widget')

class Zoom_Advanced(Frame):
    ''' Advanced zoom of the image '''
    def __init__(self, mainframe, path):
        ''' Initialize the main Frame '''
        Frame.__init__(self, master=mainframe)
        self.master.title('Zoom with mouse wheel')
        self.master.protocol('WM_DELETE_WINDOW', self.close)
        # Vertical and horizontal scrollbars for canvas
        vbar = AutoScrollbar(self.master, orient='vertical')
        hbar = AutoScrollbar(self.master, orient='horizontal')
        vbar.grid(row=0, column=1, sticky='ns')
        hbar.grid(row=1, column=0, sticky='we')
        # Create canvas and put image on it
        self.canvas = Canvas(self.master, highlightthickness=0,
                                xscrollcommand=hbar.set, yscrollcommand=vbar.set)
        self.canvas.grid(row=0, column=0, sticky='nswe')
        self.canvas.update()  # wait till canvas is created
        vbar.configure(command=self.scroll_y)  # bind scrollbars to the canvas
        hbar.configure(command=self.scroll_x)
        # Make the canvas expandable
        self.master.rowconfigure(0, weight=1)
        self.master.columnconfigure(0, weight=1)
        # Bind events to the Canvas
        self.canvas.bind('<Configure>', self.show_image)  # canvas is resized
        self.canvas.bind('<ButtonPress-1>', self.move_from)
        self.canvas.bind('<B1-Motion>',     self.move_to)
        self.canvas.bind('<MouseWheel>', self.wheel)  # with Windows and MacOS, but not Linux
        self.canvas.bind('<Button-5>',   self.wheel)  # only with Linux, wheel scroll down
        self.canvas.bind('<Button-4>',   self.wheel)  # only with Linux, wheel scroll up
        self.image = Image.open(path)  # open image
        self.width, self.height = self.image.size
        self.imscale = 1.0  # scale for the canvaas image
        self.delta = 1.3  # zoom magnitude
        # Put image into container rectangle and use it to set proper coordinates to the image
        self.container = self.canvas.create_rectangle(0, 0, self.width, self.height, width=0)

        self.show_image()

    def scroll_y(self, *args, **kwargs):
        ''' Scroll canvas vertically and redraw the image '''
        self.canvas.yview(*args, **kwargs)  # scroll vertically
        self.show_image()  # redraw the image

    def scroll_x(self, *args, **kwargs):
        ''' Scroll canvas horizontally and redraw the image '''
        self.canvas.xview(*args, **kwargs)  # scroll horizontally
        self.show_image()  # redraw the image

    def move_from(self, event):
        ''' Remember previous coordinates for scrolling with the mouse '''
        self.canvas.scan_mark(event.x, event.y)

    def move_to(self, event):
        ''' Drag (move) canvas to the new position '''
        self.canvas.scan_dragto(event.x, event.y, gain=1)
        self.show_image()  # redraw the image

    def wheel(self, event):
        ''' Zoom with mouse wheel '''
        x = self.canvas.canvasx(event.x)
        y = self.canvas.canvasy(event.y)

        #print event.delta

        bbox = self.canvas.bbox(self.container)  # get image area
        if bbox[0] < x < bbox[2] and bbox[1] < y < bbox[3]: pass  # Ok! Inside the image
        else: return  # zoom only inside image area
        scale = 1.0
        # Respond to Linux (event.num) or Windows (event.delta) wheel event
        if event.num == 5 or event.delta < 0:  # scroll down
            i = min(self.width, self.height)
            if int(i * self.imscale) < 30: return  # image is less than 30 pixels
            self.imscale /= self.delta
            scale        /= self.delta
        if event.num == 4 or event.delta > 00:  # scroll up
            i = min(self.canvas.winfo_width(), self.canvas.winfo_height())
            if i < self.imscale: return  # 1 pixel is bigger than the visible area
            self.imscale *= self.delta
            scale        *= self.delta
        self.canvas.scale('all', x, y, scale, scale)  # rescale all canvas objects
        self.show_image()

    def show_image(self, event=None):
        ''' Show image on the Canvas '''
        bbox1 = self.canvas.bbox(self.container)  # get image area
        # Remove 1 pixel shift at the sides of the bbox1
        bbox1 = (bbox1[0] + 1, bbox1[1] + 1, bbox1[2] - 1, bbox1[3] - 1)
        bbox2 = (self.canvas.canvasx(0),  # get visible area of the canvas
                 self.canvas.canvasy(0),
                 self.canvas.canvasx(self.canvas.winfo_width()),
                 self.canvas.canvasy(self.canvas.winfo_height()))
        bbox = [min(bbox1[0], bbox2[0]), min(bbox1[1], bbox2[1]),  # get scroll region box
                max(bbox1[2], bbox2[2]), max(bbox1[3], bbox2[3])]
        if bbox[0] == bbox2[0] and bbox[2] == bbox2[2]:  # whole image in the visible area
            bbox[0] = bbox1[0]
            bbox[2] = bbox1[2]
        if bbox[1] == bbox2[1] and bbox[3] == bbox2[3]:  # whole image in the visible area
            bbox[1] = bbox1[1]
            bbox[3] = bbox1[3]
        self.canvas.configure(scrollregion=tuple(bbox))  # set scroll region
        x1 = max(bbox2[0] - bbox1[0], 0)  # get coordinates (x1,y1,x2,y2) of the image tile
        y1 = max(bbox2[1] - bbox1[1], 0)
        x2 = min(bbox2[2], bbox1[2]) - bbox1[0]
        y2 = min(bbox2[3], bbox1[3]) - bbox1[1]
        if int(x2 - x1) > 0 and int(y2 - y1) > 0:  # show image if it in the visible area
            x = min(int(x2 / self.imscale), self.width)   # sometimes it is larger on 1 pixel...
            y = min(int(y2 / self.imscale), self.height)  # ...and sometimes not
            image = self.image.crop((int(x1 / self.imscale), int(y1 / self.imscale), x, y))
            imagetk = ImageTk.PhotoImage(image.resize((int(x2 - x1), int(y2 - y1))))
            imageid = self.canvas.create_image(max(bbox2[0], bbox1[0]), max(bbox2[1], bbox1[1]),
                                               anchor='nw', image=imagetk)
            self.canvas.lower(imageid)  # set image into background
            self.canvas.imagetk = imagetk  # keep an extra reference to prevent garbage-collection
    def close(self):
        return

    def hide(self):
        self.master.withdraw()

    def show(self):
        self.master.update()
        self.master.deiconify()

# popup window for the options dialog
class optionsPopupWindow(object):
    # options as they are are passed in upon the creation of the window
    def __init__(self, master, smoothing_methods, smoothing_parameters, percentile, write_diameters, smoothing_method, drawWidth):
        self.top=self.top=Toplevel(master)
        self.top.resizable(width=FALSE, height=FALSE)
        self.top.wm_title("Options")
        self.top.protocol('WM_DELETE_WINDOW', self.cleanup)

        self.top.bind('<Return>', self.cleanup)

        params = smoothing_parameters[smoothing_methods.index(smoothing_method)]

        self.smoothingMethod = StringVar(self.top)
        self.smoothingMethod.set(smoothing_method)

        general = LabelFrame(self.top, text = 'General options', padx = 5, pady = 5, fg = '#56A0D3')
        general.grid(row = 0, padx = 10, pady = 5, sticky = EW)

        self.wdiams = IntVar(self.top)
        self.wdiams.set(0)

        self.drawWidth = IntVar(self.top)
        self.drawWidth.set(drawWidth)

        self.acc_p = StringVar(self.top)
        self.acc_p.set(str(percentile))

        if write_diameters:
            self.wdiams.set(1)

        Label(general, text = 'Drawing thickness (pixels): ').grid(row = 0, padx = 5, pady = 5)
        self.drawWidth_entry = Entry(general, textvariable = self.drawWidth, width = 10, bd = 3)
        self.drawWidth_entry.grid(row = 0, column = 1, padx = 5)

        c = Checkbutton(general, text="Compute and write diameter info", variable=self.wdiams)
        c.grid(row = 1, padx = 5, pady = 5)

        Label(general, text = 'Percentile of acceleration histogram:').grid(row = 2, padx = 5, pady = 5)
        self.acc_p_entry = Entry(general, textvariable = self.acc_p, width = 10, bd = 3)
        self.acc_p_entry.grid(row = 2, column = 1, padx = 5)

        parameters = LabelFrame(self.top, text="Smoothing parameters", padx=5, pady=5,  fg = '#56A0D3')

        Label(self.top, text = 'Smoothing method: ').grid(row = 1, column = 0, padx = 10, pady = 5, sticky = W)
        self.sm = OptionMenu(self.top, self.smoothingMethod, *smoothing_methods)
        self.sm.grid(row = 1, column = 0, sticky = W, padx = 155, pady = 10)

        parameters.grid(row = 2, padx = 10, pady = 5, sticky = EW)

        if smoothing_method == 'Chanvese':
            self.alphaVal = StringVar(self.top)
            self.alphaVal.set(str(params['alpha']))

            self.tolerance = StringVar(self.top)
            self.tolerance.set(str(params['pixel_error_tolerance']))

            self.max_its = StringVar(self.top)
            self.max_its.set(str(params['max_its']))

            Label(parameters, text = 'Alpha (higher = smoother): ').grid(row = 0, column = 0, padx = 5, pady = 5, sticky = W)
            self.alpha = Entry(parameters, textvariable = self.alphaVal, width = 10, bd = 3)
            self.alpha.grid(row = 0, padx = 200, pady = 5, sticky = W)

            Label(parameters, text = 'Error tolerance (pixels):').grid(row = 1, column = 0, padx = 5, pady = 5, sticky = W)
            self.tol = Entry(parameters, textvariable = self.tolerance, width = 10, bd = 3)
            self.tol.grid(row = 1, padx = 200, pady = 5, sticky = W)

            Label(parameters, text = 'Max iterations: ').grid(row = 2, column = 0, padx = 5, pady = 5, sticky = W)
            self.tol = Entry(parameters, textvariable = self.max_its, width = 10, bd = 3)
            self.tol.grid(row = 2, padx = 200, pady = 5, sticky = W)


        OK = Button(self.top, text = 'OK', command = self.cleanup)
        OK.grid(row = 3, column = 0, sticky = W, padx = 10, pady = 10)

    def cleanup(self, event = None):
        self.top.destroy()

class transformWindow(object):
    # options as they are are passed in upon the creation of the window
    def __init__(self, master, gui_object):
        self.top=self.top=Toplevel(master)
        self.top.resizable(width=FALSE, height=FALSE)
        self.top.wm_title("Transforms")
        self.top.protocol('WM_DELETE_WINDOW', self.hide)

        self.gui_object = gui_object

        tooltips = Pmw.Balloon(self.top)
        self.argnames = ['ksize = {0}']

        self.arg1 = StringVar(self.top)
        self.arg1.set('5')

        self.arg2 = StringVar(self.top)
        self.arg2.set('5')

        self.arg3 = StringVar(self.top)
        self.arg3.set('5')

        self.transformVar = StringVar(self.top)
        self.transformVar.set('Average Blur')

        Label(self.top, text = 'Transform:').grid(row = 0, padx = 10, pady = 5, sticky = 'W')
        method = OptionMenu(self.top, self.transformVar, 'Average Blur', 'Gaussian Blur', 'Median Blur', 'Bilateral Filter', command = self.callback)
        method.grid(row = 0, padx = 100, pady = 10, sticky = 'W')

        self.general = LabelFrame(self.top, text = 'Parameters', padx = 5, pady = 5, fg = '#56A0D3')

        self.args = [self.arg1, self.arg2, self.arg3]

        self.arg1_label = Label(self.general, text = 'Kernel size (pixels):')
        self.arg1_label.grid(row = 0, padx = 10, pady = 5, sticky = 'W')
        self.arg1_entry = Entry(self.general, textvariable = self.arg1, width = 5)
        self.arg1_entry.grid(row = 0, padx = 145, sticky = 'W')

        self.arg2_label = Label(self.general, text = 'sigmaColor:')
        self.arg2_label.grid(row = 1, padx = 10, pady = 5, sticky = 'W')
        self.arg2_entry = Entry(self.general, textvariable = self.arg2, width = 5)
        self.arg2_entry.grid(row = 1, padx = 125, sticky = 'W')

        self.arg3_label = Label(self.general, text = 'sigmaSpace:')
        self.arg3_label.grid(row = 2, padx = 10, pady = 5, sticky = 'W')
        self.arg3_entry = Entry(self.general, textvariable = self.arg3, width = 5)
        self.arg3_entry.grid(row = 2, padx = 125, sticky = 'W')

        self.general.grid(row = 1, padx = 10, pady = 5, sticky = EW)

        self.callback(None)

        self.filelist = Listbox(self.top, width = 50, height = 10)
        self.filelist.grid(row = 3, column = 0, padx = 5, pady = 5, sticky = EW)
        tooltips.bind(self.filelist, "List of transforms applied to the image\nPress '+' button to add a transform")

        findInFile = Button(self.top, text = " + ", command = self.add, padx = 10, pady = 10)
        findInFile.grid(row = 2, column = 0, sticky = E, padx = 5, pady = 5)
        tooltips.bind(findInFile, "Add transform")

        clearButton = Button(self.top, text = "Clear all", command = self.clear, padx = 10, pady = 5)
        clearButton.grid(row = 2, column = 0, padx = 5, pady = 5)

        delButton = Button(self.top, text = " - ",
                   command=self.delete, padx = 10, pady = 10)
        delButton.grid(row = 2, column = 0, sticky = W, padx = 5, pady = 5)
        tooltips.bind(delButton, "Remove a transform")

    def get_current(self):
        ret = self.transformVar.get()
        options = dict()

        for i in range(len(self.argnames)):
            ret += ', {0} = {1}'.format(self.argnames[i], self.args[i].get())
            if i == 0:
                options[self.argnames[i]] = int(self.args[i].get())
            else:
                options[self.argnames[i]] = float(self.args[i].get())

        if 'Morphological' in self.transformVar.get():
            options['transform'] = self.transformVar.get().split(' ')[-1]

        return ret, [self.transformVar.get(), options]

    def clear(self):
        self.filelist.delete(0, END)

        self.gui_object.transformer.options = []
        self.gui_object.callback()

    def add(self):
        string, option = self.get_current()
        self.filelist.insert(END, string)

        self.gui_object.transformer.options.append(option)
        self.gui_object.callback()
        return

    def delete(self):
        if self.filelist.get(ANCHOR) != '':
            del self.gui_object.transformer.options[self.filelist.get(0, END).index(self.filelist.get(ANCHOR))]
            self.filelist.delete(ANCHOR)
        elif self.filelist.get(END) != '':
            del self.gui_object.transformer.options[-1]
            self.filelist.delete(END)

        self.gui_object.callback()
        return

    def callback(self, event):

        if self.transformVar.get() == 'Average Blur' or self.transformVar.get() == 'Median Blur' or 'Morphological' in self.transformVar.get():
            self.arg1_label.grid(row = 0, padx = 10, pady = 5, sticky = 'W')
            self.arg1_entry.grid(row = 0, padx = 145, sticky = 'W')

            self.arg1_label.config(text = 'Kernel size (pixels):')
            self.arg1.set('5')

            self.arg2_label.grid_forget()
            self.arg2_entry.grid_forget()

            self.arg3_label.grid_forget()
            self.arg3_entry.grid_forget()

            self.argnames = ['ksize']

        elif self.transformVar.get() == 'Gaussian Blur':
            self.arg2_label.grid(row = 1, padx = 10, pady = 5, sticky = 'W')
            self.arg2_entry.grid(row = 1, padx = 125, sticky = 'W')

            self.arg3_label.grid(row = 2, padx = 10, pady = 5, sticky = 'W')
            self.arg3_entry.grid(row = 2, padx = 125, sticky = 'W')

            self.arg1_label.config(text = 'Kernel size (pixels):')
            self.arg2_label.config(text = 'SigmaX:')
            self.arg3_label.config(text = 'SigmaY:')

            self.arg1.set('5')
            self.arg2.set('0.')
            self.arg3.set('0.')
            self.argnames = ['ksize', 'SigmaX', 'SigmaY']
        elif self.transformVar.get() == 'Bilateral Filter':
            self.arg1_label.grid(row = 0, padx = 10, pady = 5, sticky = 'W')
            self.arg1_entry.grid(row = 0, padx = 145, sticky = 'W')

            self.arg2_label.grid(row = 1, padx = 10, pady = 5, sticky = 'W')
            self.arg2_entry.grid(row = 1, padx = 125, sticky = 'W')

            self.arg3_label.grid(row = 2, padx = 10, pady = 5, sticky = 'W')
            self.arg3_entry.grid(row = 2, padx = 125, sticky = 'W')

            self.arg1_label.config(text = 'Kernel size (pixels):')
            self.arg2_label.config(text = 'SigmaColor:')
            self.arg3_label.config(text = 'SigmaSpace:')

            self.arg1.set('5')
            self.arg2.set('75')
            self.arg3.set('75')

            self.argnames = ['d', 'sigmaSpace', 'sigmaColor']
        elif self.transformVar.get() == 'Adaptive Gaussian Threshold':
            self.arg1_label.config(text = 'Block size (pixels)')

            self.arg1.set('11')

            self.arg2_label.grid_forget()
            self.arg2_entry.grid_forget()

            self.arg3_label.grid_forget()
            self.arg3_entry.grid_forget()

            self.argnames = ['blockSize']
        elif self.transformVar.get() == 'Otsu Threshold':
            self.arg1_label.grid_forget()
            self.arg1_entry.grid_forget()

            self.arg2_label.grid_forget()
            self.arg2_entry.grid_forget()

            self.arg3_label.grid_forget()
            self.arg3_entry.grid_forget()

            self.argnames = []

    def hide(self):
        self.top.withdraw()

    def show(self):
        self.top.update()
        self.top.deiconify()

class Transformer(object):
    def __init__(self, gui_object):
        self.options = []
        self.gui_object = gui_object

    def average_blur(self, im, ksize = 5):
        return cv2.blur(im, (ksize, ksize))

    def gaussian_blur(self, im, ksize, SigmaX, SigmaY):
        return cv2.GaussianBlur(im, (ksize, ksize), SigmaX, SigmaY)

    def median_blur(self, im, ksize = 5):
        return cv2.medianBlur(im, ksize)

    def laplacian(self, im, ksize = 5):
        ret = cv2.Laplacian(im, cv2.CV_64F, ksize = ksize)
        ret = ret - np.min(ret)
        ret /= np.max(ret)

        return np.round(ret*255).astype(np.uint8)

    def bilateral_filter(self, im, d = 9, sigmaColor = 75, sigmaSpace = 75):
        return cv2.bilateralFilter(im, d, sigmaColor, sigmaSpace)

    def adaptive_gaussian_threshold(self, im, blockSize = 11):
        return cv2.adaptiveThreshold(im, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, blockSize, 2)

    def otsu_threshold(self, im):
        ret, thresh = cv2.threshold(im, 0, 255, cv2.THRESH_BINARY+cv2.THRESH_OTSU)
        return thresh

    def morph_transform(self, im, ksize, transform = 'Erosion'):
        kernel = np.ones((ksize, ksize), dtype = np.uint8)

        if transform == 'Erosion':
            return cv2.erode(im, kernel, iterations = 1)
        elif transform == 'Dilation':
            return cv2.dilate(im, kernel, iterations = 1)
        elif transform == 'Closing':
            return cv2.morphologyEx(im, cv2.MORPH_CLOSE, kernel)
        elif transform == 'Opening':
            return cv2.morphologyEx(im, cv2.MORPH_OPEN, kernel)

    def transform(self, ret):
        self.gui_object.manualThresh = True

        for o in self.options:
            if o[0] == 'Average Blur':
                ret = self.average_blur(ret, **o[1])
            elif o[0] == 'Gaussian Blur':
                ret = self.gaussian_blur(ret, **o[1])
            elif o[0] == 'Median Blur':
                ret = self.median_blur(ret, **o[1])
            elif o[0] == 'Bilateral Filter':
                ret = self.bilateral_filter(ret, **o[1])
            elif o[0] == 'Adaptive Gaussian Threshold':
                ret = self.adaptive_gaussian_threshold(ret, **o[1])
                self.gui_object.manualThresh = False
            elif o[0] == 'Otsu Threshold':
                ret = self.otsu_threshold(ret)
                self.gui_object.manualThresh = False

        self.gui_object.set_state()

        return ret

class ContourizeMe(object):
    def __init__(self, im_path):
        """
        ----------------
        Global variables
        ----------------

        Set the defaults:
        """
        # List of bezier curves
        self.beziers = None

        # Thresheld image given user constraints
        self.thresh = None

        # Image to threshold given user constraints (Grayscale, RGB, or HSV)
        # after potential transforms
        self.tothresh = None

        # List of finalized (potentially smoothed contour points), a list of N,2 arrays representing each contour in pixel space
        self.outs = None

        tcks = []

        # Approximate arc lenghth per Bezier curve
        self.pp = 15.

        # Boolean for writing and visualizing estimated diameters
        self.write_diameters = True

        # Lower bound for the percetile of accelerations to be considered for diameter calculation
        self.percentile = 100.

        # Smoothing algorithm options
        # set the default options
        self.smoothing_methods = ['Chanvese', 'None']
        self.smoothing_method = 'Chanvese'
        self.smoothing_parameters = [{'alpha': 0.01, 'pixel_error_tolerance': 10, 'max_its': 5}, dict()]

        self.smoothing = False

        """
        Begin loadin the data and GUI elements
        """
        # Load the image
        self.im = cv2.imread(im_path)
        self.transformer = Transformer(self)
        self.manualThresh = True
        self.hidden = True

        # Keep the three paramaterizations in memory
        # -----------------------
        # gray = self.imgray
        # BGR = self.im
        # HSV = self.hsv_im

        if self.im is None:
            # read with the alternate method
            self.im = imread(os.path.abspath(im_path))

            if len(np.where(self.im > 255)[0]) > 0:
                self.im = map_uint16_to_uint8(self.im)
            self.imgray = cv2.cvtColor(self.im, cv2.COLOR_BGR2GRAY)
        elif len(self.im.shape) == 3:
            self.imgray = cv2.cvtColor(self.im, cv2.COLOR_BGR2GRAY)
        else:
            self.imgray = copy.copy(self.im)
            self.im = cv2.cvtColor(self.imgray, cv2.COLOR_GRAY2BGR)
            logger.info('Working with grayscale image')

        self.info = dict()
        self.info['Image location'] = os.path.abspath(im_path)
        self.mask = np.zeros(self.imgray.shape, dtype = np.uint8)

        # to display
        self.mim = cv2.cvtColor(copy.copy(self.im), cv2.COLOR_BGR2RGB)

        # Get HSV paramaterization
        self.hsv_im = cv2.cvtColor(copy.copy(self.im), cv2.COLOR_BGR2HSV)

        ret, thresh = cv2.threshold(self.imgray, 127, 255, 0)
        _ = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

        # OpenCV 2 patch
        if len(_) == 3:
            _, contours, hierarchy = _
        else:
            contours, hierarchy = _

        self.contours = sorted(contours, key = len, reverse = True)
        for j in range(1):
            cv2.drawContours(self.mim, contours, j, color=(0, 0, 0), thickness=-1)

        # Create the window
        self.root = Tk()
        self.root.resizable(width=False, height=False)

        view_screen = Toplevel(self.root)
        view_screen.resizable(width=TRUE, height=TRUE)

        t_view_screen = Toplevel(self.root)
        t_view_screen.resizable(width=TRUE, height=TRUE)
        # set the title
        self.root.wm_title('ContourizeMe')

        # View screen window
        self.app = Zoom_Advanced(view_screen, path=im_path)
        self.t_app = Zoom_Advanced(t_view_screen, path=im_path)
        self.t_app.hide()

        self.pamVar = StringVar()
        self.pamVar.set('Grayscale')

        self.nContours = StringVar()
        self.nContours.set('1')
        self.allContours = IntVar()

        self.drawWidth = 1

        self.nContours.trace('w', lambda *args: self.callback())

        self.w4 = Scale(self.root, from_=3, to=300, orient=HORIZONTAL, command = self.callback)
        self.w4.set(int(self.pp))

        #kernelSize.trace("w", lambda name, index, mode, kernelSize=kernelSize: callback(kernelSize))

        self.root.protocol('WM_DELETE_WINDOW', self.quit_all)

        Label(self.root, text = 'Gray / Red / Hue').grid(row = 6, column = 0, columnspan = 2, padx = 5, pady = 10, sticky = 'EW')
        self.w1 = Scale(self.root, from_=0, to=255, orient=VERTICAL, command = self.callback, length = 500)
        self.w1.set(0)
        self.w1.grid(row = 0, column = 0, padx = 10, pady = 5, sticky = 'NS', rowspan = 6)
        self.w2 = Scale(self.root, from_=0, to=255, orient=VERTICAL, command = self.callback, length = 500)
        self.w2.set(255)
        self.w2.grid(row = 0, column = 1,  padx = 10, pady = 5, sticky = 'NS', rowspan = 6)

        Label(self.root, text = 'Green / Saturation').grid(row = 6, column = 2, columnspan = 2, padx = 5, pady = 10, sticky = 'EW')
        self.w5 = Scale(self.root, from_=0, to=255, orient=VERTICAL, command = self.callback, length = 500)
        self.w5.set(0)
        self.w5.grid(row = 0, column = 2, padx = 10, pady = 5,  sticky = 'NS', rowspan = 6)
        self.w6 = Scale(self.root, from_=0, to=255, orient=VERTICAL, command = self.callback, length = 500)
        self.w6.set(255)
        self.w6.grid(row = 0, column = 3,  padx = 10, pady = 5,  sticky = 'NS', rowspan = 6)

        Label(self.root, text = 'Blue / Value').grid(row = 6, column = 4, columnspan = 2, padx = 5, pady = 10, sticky = 'EW')
        self.w7 = Scale(self.root, from_=0, to=255, orient=VERTICAL, command = self.callback, length = 500)
        self.w7.set(0)
        self.w7.grid(row = 0, column = 4, padx = 10, pady = 5,  sticky = 'NS', rowspan = 6)
        self.w8 = Scale(self.root, from_=0, to=255, orient=VERTICAL, command = self.callback, length = 500)
        self.w8.set(255)
        self.w8.grid(row = 0, column = 5,  padx = 10, pady = 5,  sticky = 'NS', rowspan = 6)

        Label(self.root, text = 'Number of contours to show:').grid(row = 7, padx = 10, columnspan = 6, sticky = 'W')
        self.w3 = Entry(self.root, textvariable = self.nContours, width = 5, command = self.callback()).grid(row = 7, columnspan = 6, padx = 210, sticky = 'W')

        c = Checkbutton(self.root, text="Show all contours", variable=self.allContours, command = self.callback)
        c.grid(row = 7, padx = 285, pady = 10, sticky = 'W', columnspan = 6)

        """
        Label(self.root, text = 'Number of contours to show:').grid(row = 7, padx = 10, columnspan = 6, sticky = 'W')
        self.w3 = Scale(self.root, from_=1, to=10, orient=HORIZONTAL, command = self.callback)
        self.w3.set(1)
        self.w3.grid(row = 8, padx = 10, pady = 5, sticky = 'EW', columnspan = 6)
        """

        Label(self.root, text = 'Perimeter per Bezier:').grid(row = 9, padx = 10, columnspan = 6, sticky = 'W')
        self.w4.set(int(self.pp))
        self.w4.grid(row = 10, padx = 10, pady = 5, sticky = 'EW', columnspan = 6)

        self.buttons = LabelFrame(self.root, text = 'Operations', padx = 5, pady = 5, fg = '#56A0D3')
        self.buttons.grid(row = 11, columnspan = 6, sticky = 'EW', padx = 5, pady = 10)

        Label(self.buttons, text = 'Parameterization:').grid(row = 0, column = 0, padx = 10, pady = 5, sticky = 'W')
        method = OptionMenu(self.buttons, self.pamVar, 'Grayscale', 'RGB', 'HSV', command = self.callback)
        method.grid(row = 0, column = 0, padx = 125, pady = 5, sticky = 'W')

        save = Button(self.buttons, text = "Save to SVG", command = self.save_to_svg)
        save.grid(row = 2, column = 0, padx = 10, pady = 5, sticky = 'W')

        options = Button(self.buttons, text = 'Options', command = self.opfunc)
        options.grid(row = 2, column = 0, padx = 125, pady = 5, sticky = 'W')

        save = Button(self.buttons, text = "Plot", command = self.plot_beziers)
        save.grid(row = 2, column = 0, padx = 200, pady = 5, sticky = 'W')

        transforms = Button(self.buttons, text = 'Transforms', command = self.tfunc)
        transforms.grid(row = 2, column = 0, padx = 250, pady = 5, sticky = 'W')

        self.hideShowTransformedImage = Button(self.buttons, text = 'Show transformed image', command = self.hide_show)
        self.hideShowTransformedImage.grid(row = 2, column = 0, padx = 350, pady = 5, sticky = 'W')

        self.transformWindow = transformWindow(self.root, self)
        self.transformWindow.hide()

        self.root.mainloop()

    def callback(self, e = None):
        tothresh = self.get_tothresh()

        self.pp = float(self.w4.get())

        _ = copy.copy(self.mim)

        if tothresh is not None:
            if not self.smoothing:
                self.contours, self.thresh = self.get_contours(tothresh)

            cv2.drawContours(_, self.contours, -1, color=(0, 255, 0), thickness=self.drawWidth)

            img = Image.fromarray(_)
            img_t = Image.fromarray(tothresh)
            #img = ImageTk.PhotoImage(img)

            self.app.image = img
            self.app.show_image()

            self.t_app.image = img_t
            self.t_app.show_image()

    def get_tothresh(self):
        if self.pamVar.get() == 'Grayscale':
            return self.transformer.transform(self.imgray)
        elif self.pamVar.get() == 'RGB':
            return self.transformer.transform(self.im)
        elif self.pamVar.get() == 'HSV':
            return self.transformer.transform(self.hsv_im)


    def get_bounds(self):
        # Grab the chosen bounds
        r1 = int(np.round(self.w1.get()))
        r2 = int(np.round(self.w2.get()))

        b1 = int(np.round(self.w5.get()))
        b2 = int(np.round(self.w6.get()))

        g1 = int(np.round(self.w7.get()))
        g2 = int(np.round(self.w8.get()))

        return r1, r2, b1, b2, g1, g2

    def set_state(self):
        if not self.manualThresh:
            self.w1.config(state = DISABLED)
            self.w2.config(state = DISABLED)
            self.w5.config(state = DISABLED)
            self.w6.config(state = DISABLED)
            self.w7.config(state = DISABLED)
            self.w8.config(state = DISABLED)
        else:
            self.w1.config(state = NORMAL)
            self.w2.config(state = NORMAL)
            self.w5.config(state = NORMAL)
            self.w6.config(state = NORMAL)
            self.w7.config(state = NORMAL)
            self.w8.config(state = NORMAL)

    def get_contours(self, tothresh):
        r1, r2, b1, b2, g1, g2 = self.get_bounds()

        # Bound according to the chosen paramaterization
        if self.manualThresh:
            if self.pamVar.get() == 'Grayscale':
                thresh = cv2.inRange(tothresh, r1, r2)

            elif self.pamVar.get() == 'RGB':
                thresh = cv2.inRange(tothresh, (b1, g1, r1), (b2, g2, r2))
            elif self.pamVar.get() == 'HSV':
                thresh = cv2.inRange(tothresh, (r1, g1, b1), (r2, g2, b2))
        else:
            thresh = tothresh

        # contour finding with OpenCV 2 or 3
        _ = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

        if len(_) == 3:
            _, contours, hierarchy = _
        else:
            contours, hierarchy = _

        contours = sorted(contours, key = len, reverse = True)

        if self.allContours.get() != 1:
            try:
                nContours = int(self.nContours.get())

                if len(contours) > nContours:
                    contours = contours[:nContours]
            except:
                pass

        return contours, thresh

    def quit_all(self):
        self.root.quit()
        self.root.destroy()
        plt.close()
        sys.exit()

    def plot_beziers(self, plot = True, ofile = None):
        plt.clf()
        logger.info('Creating bezier curves...')

        self.outs = []
        self.beziers = []

        mask = np.zeros(self.imgray.shape)
        cv2.drawContours(mask, self.contours, -1, color = 1., thickness = -1)

        params = self.smoothing_parameters[self.smoothing_methods.index(self.smoothing_method)]

        c = Chanvese()
        seg, phi, its = c.chanvese(self.imgray, mask, alpha = params['alpha'], max_its = params['max_its'], display = False, thresh = params['pixel_error_tolerance'])

        cs = plt.contour(phi, 0)
        for collection in cs.collections:
            paths = collection.get_paths()
            for path in paths:
                self.outs.append(path.vertices)


        for out in self.outs:
            c =  out.reshape(len(out), 1, 2).astype(np.float32)

            perimeter = cv2.arcLength(c, True)

            #print perimeter

            als = np.array([0.] + [cv2.arcLength(c[:i], True) for i in range(1, len(c))])

            t = np.linspace(0., perimeter, int(np.round(perimeter / self.pp)) * 2 + 1)
            t = [np.argmin(np.abs(als - u)) for u in t]

            for k in range(out.shape[0] // 2):
                b = out[2*k:2*(k + 1) + 1,:]


                if len(b) == 3:
                    self.beziers.append(b)


        if plot:
            logger.info('Plotting...')

            plt.gca().invert_yaxis()

            for b in self.beziers:
                t = np.linspace(0., 1., 6)
                xy = np.array([cubic_smooth_bezier(b, u) for u in t])

                plt.plot(xy[:, 0], xy[:, 1], c = 'b')

            plt.show()
            plt.close()

    def opfunc(self):
        # make an options window and wait for it
        root = Tk()
        root.withdraw()

        w = optionsPopupWindow(root, self.smoothing_methods, self.smoothing_parameters, self.percentile, self.write_diameters, self.smoothing_method, self.drawWidth)
        root.wait_window(w.top)

        if w.wdiams.get() == 1:
            self.write_diameters = True
        else:
            self.write_diameters = False

        self.percentile = float(w.acc_p.get())

        self.drawWidth = w.drawWidth.get()

        self.smoothing_method = w.smoothingMethod.get()
        params = self.smoothing_parameters[self.smoothing_methods.index(self.smoothing_method)]

        if self.smoothing_method == 'Chanvese':
            params['alpha'] = float(w.alphaVal.get())
            params['pixel_error_tolerance'] = int(w.tolerance.get())
            params['max_its'] = int(w.max_its.get())

        self.smoothing_parameters[self.smoothing_methods.index(self.smoothing_method)] = params

    def tfunc(self):
        self.transformWindow.show()

    def save_to_svg(self):
        plt.clf()
        if len(self.contours) > 0:
            try:
                filename = filedialog.asksaveasfilename()
            except:
                filename = tkinter.filedialog.asksaveasfilename()

            if type(filename) == str and filename != '':
                self.plot_beziers(plot = False)

                mask = np.zeros(self.imgray.shape)
                cv2.drawContours(mask, self.contours, -1, color = 1., thickness = -1)

                logger.info('Computing normal vectors and diameter...')
                if self.write_diameters:
                    dataf, xys, diameters, nvs, si = get_diameters(self.outs, self.beziers, mask, acc_bound = self.percentile)

                    xx1 = dataf['x1']
                    yy1 = dataf['y1']
                    xx2 = dataf['x2']
                    yy2 = dataf['y2']

                    for k in range(len(xx1)):
                        x1 = xx1[k]
                        y1 = yy1[k]
                        x2 = xx2[k]
                        y2 = yy2[k]

                        plt.plot([x1, x2], [y1, y2], c = 'b')

                    plt.ylim(np.max(yy2) + 50, 0)

                paths = []
                for b in self.beziers:
                    x1, y1 = b[0]
                    if (5. < x1 < self.im.shape[1] - 5) and (5. < y1 < self.im.shape[0]):
                        cx2, cy2 = b[1]
                        x2, y2 = b[2]
                        paths.append(CubicBezier(x1 + 1j * y1, x1 + 1j * y1, cx2 + 1j * cy2, x2 + 1j * y2))


                logger.info(('Writing SVG file to "{}"'.format(filename + '.svg')))

                wsvg(paths, filename = filename + '.svg')

                # Update the information dictionary
                self.update_info()

                if self.smoothing_method != 'None':
                    ofile = Contours(self.contours, self.beziers, self.info, self.outs)
                else:
                    ofile = Contours(self.contours, self.beziers, self.info)

                pickle.dump(ofile, open('{0}.pkl'.format(filename), 'wb'))

                dataf = pd.DataFrame(dataf)
                dataf.to_csv(filename + '-diameters.csv', index = False)

                plt.savefig(filename + '-diameters.png', dpi = 100)
                logger.info('Done!')

    def update_info(self):
        r1, r2, b1, b2, g1, g2 = self.get_bounds()

        self.info['Parameterization'] = self.pamVar.get()

        # Bound according to the chosen paramaterization
        if self.pamVar.get() == 'Grayscale':
            self.info['Lower bound'] = r1
            self.info['Upper bound'] = r2
        else:
            self.info['Lower bound'] = (r1, g1, b1)
            self.info['Upper bound'] = (r2, g2, b2)

        self.info['Transforms'] = self.transformer.options

        self.info['Smoothing'] = [self.smoothing_method, self.smoothing_parameters[self.smoothing_methods.index(self.smoothing_method)]]

    def hide_show(self):
        if self.hidden:
            self.t_app.show()
            self.hideShowTransformedImage.config(text = 'Hide transformed image')

            self.hidden = False
        else:
            self.t_app.hide()
            self.hideShowTransformedImage.config(text = 'Show transformed image')

            self.hidden = True




# This main function is an "entry point" for the program as defined in
# setup.py . The function must not take any arguments, so we must
# read any command line arguments from sys.argv instead.
def main(args=None):
    if args is None:
        args = sys.argv[1:]

    parser = argparse.ArgumentParser(description="allows the user to slide to a values for 8-bit pixel thresholding")
    parser.add_argument("image", default = "None")
    parser.add_argument("--movie", default = "None")
    parser.add_argument("--scale", default = "0.5")

    args = parser.parse_args()
    ContourizeMe(args.image)
