"""
MMeSamplePixels
---------------

Description:
Displays an image and allows users to click on the foreground and the background
for the purpose of sampling regions to later solve and SVC (Support Vector Classifier)
Making a model of the foreground and background in a set of images is an optional
part of the workflow included in MeshmerizeMe to estimate contours as 2D meshes.

Example:

MMeSamplePixels leaf.jpg

Args:
    image: the image to be sampled. Any format capable of being read by OpenCV is OK.

"""


import six.moves.tkinter_tkfiledialog as tkFileDialog
import six.moves.tkinter_messagebox
from six.moves.tkinter import *
from threading import Thread
from six.moves import map
from six.moves import range

if sys.platform == 'darwin':
    root = Tk()
    root.withdraw()
    root.quit()

import pyglet
from pyglet.window import key
from pyglet.gl import *
import time

from pyglet.gl import *
from pyglet.graphics import *
from pygarrayimage.arrayimage import ArrayInterfaceImage

from scipy.sparse import lil_matrix, csc_matrix

import argparse
import math
import copy

import cv2
import numpy as np
import pickle

# modified versions of code in pgedraw. returns vertices rather than having them as an attribute of a class
def Circle(xxx_todo_changeme, radius, color=(255, 255, 255), batch = None, strip=False):
    
    (x, y) = xxx_todo_changeme
    mode = strip and GL_LINE_LOOP or GL_TRIANGLE_FAN
    
    radius = radius
    center = (x, y)

    vertices = [float(x), float(y)]

    for deg in range(0, 361, 2):
        angle = (deg * math.pi) / 180
        vertices.extend((x + math.sin(angle)*radius, y + math.cos(angle)*radius))

    #print(len(vertices), 'changed')

    pn = int(len(vertices) / 2)
    vertex_list = batch.add(pn, GL_POINTS, None,
            ('v2f/static', vertices),
            ('c4B/static', color*pn)
    )
    
    return vertex_list

# Zooming constants
ZOOM_IN_FACTOR = 1.2
ZOOM_OUT_FACTOR = 1/ZOOM_IN_FACTOR

MARKER_COLOR = (255, 105, 180, 200)

colors = [(228, 26, 28), (55, 126, 184), (77, 175, 74), (152, 78, 163), (255, 127, 0), (255, 255, 51), (166, 86, 40), (247, 129, 191)]

colors = [(u[0], u[1], u[2], 180) for u in colors]

trackList = ['Foreground', 'Background']
currentTrack = 'Foreground'

class SampleWindow(pyglet.window.Window):
    def __init__(self, image, factor = 2):
        self.filename = image
        
        img = cv2.imread(image)
        pyglet.window.Window.__init__(self, width=int(float(img.shape[1])/factor), height=int(float(img.shape[0])/factor), visible=True, resizable = True, vsync = True)

        self.ow = img.shape[1]
        self.oh = img.shape[0]

        self.end = self.ow*self.oh
        self.current = 1

        self.factor = factor

        img = self.format(img)

        self.points = dict()
        self.track_batch = pyglet.graphics.Batch()
        
        if img is not None:
            self.img = pyglet.sprite.Sprite(ArrayInterfaceImage(img).texture)
            self.img.x = 0
            self.img.y = 0
            self.img.scale = 2.
            #self.img.width = self.frameFinder.ow
            #sekf.img.height = self.frameFinder.oh
        else:
            self.img = None

        self.current_marker = None

        # dictionaries for storing OpenGL vertices and deleting later if needed
        self.drawnPoints = dict()

        # current mouse coordinate for getting a zoomed view finder
        self.x = 0
        self.y = 0
        self.view = None

        #Initialize camera values
        self.left   = 0
        self.right  = self.ow
        self.bottom = 0
        self.top    = self.oh
        self.zoom_level = 1
        self.zoomed_width  = self.ow
        self.zoomed_height = self.oh

        self.updateTracks()

        self.init_gl()

    # draw a new point
    def drawNew(self, x, y):
        track = currentTrack
        radius = 2

        self.points[currentTrack][self.current - 1] = np.array([x, y])
        #self.offsets_output[self.current - 1] = self.frameFinder.offset

        positions = self.points[track].A
        nz = list(set(self.points[track].nonzero()[0]))
        if self.drawnPoints[track][self.current - 1] is not None:
            self.drawnPoints[track][self.current - 1].delete()
            self.drawnPoints[track][self.current - 1] = Circle(tuple(positions[self.current - 1]), radius, colors[trackList.index(track) % len(colors)], self.track_batch)
        else:
            self.drawnPoints[track][self.current - 1] = Circle(tuple(positions[self.current - 1]), radius, colors[trackList.index(track) % len(colors)], self.track_batch)


    # format for Pyglet. Changes BGR to RGB, flips, rotates, then resizes 
    def format(self, image, size = None, bgs = None):
        # flip
        cv2.flip(image, 1, image)
        # BGR to RGB
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        
        # rotate 180
        image = np.rot90(image)
        image = np.rot90(image)

        image = cv2.resize(image, (int(float(self.ow)/self.factor), int(float(self.oh)/self.factor)))

        return image

    # only called upon loading a CSV. Pretty slow to define tons of vertices.
    def drawTracks(self):
        self.updateTracks()
        track = currentTrack

        positions = self.points[track].A
        nz = list(set(self.points[track].nonzero()[0]))

        radius = 2

        if self.current - 1 in nz:
            self.current_marker = Circle(tuple(positions[self.current - 1]), 4, MARKER_COLOR, self.track_batch)

        for k in nz:
            self.drawnPoints[track][k] = Circle(tuple(positions[k]), radius, colors[trackList.index(track) % len(colors)], self.track_batch)

    # called when the user changes tracks
    def changeTrack(self, oldTrack):
        start_time = time.clock()
        #print 'Changing track...'
        radius = 2

        for k in range(len(self.drawnPoints[oldTrack])):
            if self.drawnPoints[oldTrack][k] is not None:
                self.drawnPoints[oldTrack][k].delete()
                self.drawnPoints[oldTrack][k] = None

        positions = self.points[currentTrack].A
        nz = list(set(self.points[currentTrack].nonzero()[0]))

        if not self.current_marker is None:
            self.current_marker.delete()
            self.current_marker = None

        if self.current - 1 in nz:
            self.current_marker = Circle(tuple(positions[self.current - 1]), 4, MARKER_COLOR, self.track_batch)

        for k in nz:
            self.drawnPoints[currentTrack][k] = Circle(tuple(positions[k]), radius, colors[trackList.index(currentTrack) % 4], self.track_batch)

    def changeMarker(self):
        self.updateTracks()
        track = currentTrack
        
        positions = self.points[track].A
        nz = list(set(self.points[track].nonzero()[0]))

        if not self.current_marker is None:
            self.current_marker.delete()
            self.current_marker = None

        if self.current - 1 in nz:
            self.current_marker = Circle(tuple(positions[self.current - 1]), 4, MARKER_COLOR, self.track_batch)

    # delete a point
    def deletePoint(self):
        track = currentTrack

        if not self.current_marker is None:
            self.current_marker.delete()
            self.current_marker = None 

        if self.drawnPoints[track][self.current - 1] is not None:
            self.drawnPoints[track][self.current - 1].delete()
            self.drawnPoints[track][self.current - 1] = None

    # makes sure all the dictionaries have the proper keys
    def updateTracks(self):
        for track in trackList:
            try:
                self.points[track]
            except:
                #_ = np.zeros((self.end,2))
                #_[_ == 0] = np.nan
                self.points[track] = csc_matrix((self.end, 2))

            try:
                self.drawnPoints[track]
            except:
                self.drawnPoints[track] = list()
                for k in range(self.points[track].shape[0]):
                    self.drawnPoints[track].append(None)

    def init_gl(self):
        # Set clear color
        glClearColor(0/255, 0/255, 0/255, 0/255)

        # Set antialiasing
        glEnable( GL_LINE_SMOOTH )
        #glEnable( GL_POLYGON_SMOOTH )
        glHint( GL_LINE_SMOOTH_HINT, GL_NICEST )

        
        # Set alpha blending
        glEnable( GL_BLEND )
        glBlendFunc( GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA )
        
        # Set viewport
        glViewport( 0, 0, self.width, self.height )

        # Initialize Projection matrix
        glMatrixMode( GL_PROJECTION )
        glLoadIdentity()

        # Set orthographic projection matrix
        glOrtho( 0, self.width, 0, self.height, 1, -1 )

        # Initialize Modelview matrix
        glMatrixMode( GL_MODELVIEW )
        glLoadIdentity()

        # Save the default modelview matrix
        glPushMatrix()

    def on_draw(self):
        self.clear()
        
        glClear( GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT )
        
        # Initialize Projection matrix
        glMatrixMode( GL_PROJECTION )
        glLoadIdentity()

        # Initialize Modelview matrix
        glMatrixMode( GL_MODELVIEW )
        glLoadIdentity()

        try:
            while True:
                glPopMatrix()
        except:
            pass
        
        glPushMatrix()

        glOrtho( self.left, self.right, self.bottom, self.top, 1, -1 )

        if self.img is not None:
            self.img.draw()

        self.set_caption('Index: {0}'.format(self.current - 1))
        self.track_batch.draw()

    def on_mouse_scroll(self, x, y, dx, dy):
        # Get scale factor
        f = ZOOM_IN_FACTOR if dy > 0 else ZOOM_OUT_FACTOR if dy < 0 else 1
        # If zoom_level is in the proper range
        if .05 < self.zoom_level*f < 5:

            zoom_level = f*self.zoom_level

            mouse_x = float(x)/self.width
            mouse_y = float(y)/self.height

            mouse_x_in_world = self.left   + mouse_x*self.zoomed_width
            mouse_y_in_world = self.bottom + mouse_y*self.zoomed_height

            zoomed_width  = f*self.zoomed_width
            zoomed_height = f*self.zoomed_height

            left   = mouse_x_in_world - mouse_x*zoomed_width
            right  = mouse_x_in_world + (1 - mouse_x)*zoomed_width
            bottom = mouse_y_in_world - mouse_y*zoomed_height
            top    = mouse_y_in_world + (1 - mouse_y)*zoomed_height

            # Check bounds 
            if left >= 0 and bottom >= 0 and right <= self.ow and top <= self.oh and zoomed_width <= self.ow and zoomed_height <= self.oh:
                self.left, self.right, self.bottom, self.top, self.zoomed_width, self.zoomed_height = left, right, bottom, top, zoomed_width, zoomed_height
                self.zoom_level = zoom_level
                #self.frameFinder.update(self.left, self.bottom, self.right - self.left, self.top - self.bottom)

    def on_mouse_press(self, x, y, button, modifiers):
        if currentTrack != '' and (modifiers == 16 or modifiers == 0):
            self.drawNew(float(x)/self.width*self.zoomed_width + self.left, float(y)/self.height*self.zoomed_height + self.bottom)
            
            self.current += 1
            self.changeMarker()

    def save(self):
        filename = tkFileDialog.asksaveasfilename(filetypes = [("All files", "*.*")
                                                             ])

        pickle.dump([self.filename, self.points], open(filename, 'w'))
                    
    def on_key_press(self, symbol, modifiers):
        global currentTrack
        
        # reset to the original view of the entire frame
        if symbol == key.R:
            self.left   = 0
            self.right  = self.ow
            self.bottom = 0
            self.top    = self.oh
            self.zoom_level = 1
            self.zoomed_width  = self.ow
            self.zoomed_height = self.oh
        elif symbol == key.PERIOD:
            oldTrack = currentTrack
            if trackList.index(currentTrack) + 1 < len(trackList):
                currentTrack = trackList[trackList.index(currentTrack) + 1]
            else:
                currentTrack = trackList[0]
            
            self.changeTrack(oldTrack)
        # skips one index ahead
        elif symbol == key.F and (modifiers == 0 or modifiers == 16):
            if self.current + 1 <= self.end:
                self.current += 1
                self.changeMarker()
        # skips one index behind
        elif symbol == key.B and (modifiers == 0 or modifiers == 16):
            if self.current - 1 > 0:
                self.current -= 1
                self.changeMarker()
        # delete the point in the current frame and track
        elif symbol == key.D and (modifiers == 0 or modifiers == 16):
            positions = copy.copy(self.points[currentTrack])
            positions[self.current - 1] = np.asarray([0., 0.])
            positions.eliminate_zeros()
            self.points[currentTrack] = positions
            self.deletePoint()
        # saving points to a CSV file
        elif symbol == key.S:
            self.save()
    


# This main function is an "entry point" for the program as defined in
# setup.py . The function must not take any arguments, so we must
# read any command line arguments from sys.argv instead.
def main(args=None):
    if args is None:
        args = sys.argv[1:]

    # Argument Parser    
    parser = argparse.ArgumentParser()
    parser.add_argument("image", default = "None")

    args = parser.parse_args()

    # initate the sampling Pyglet window
    window = SampleWindow(args.image)

    # run the mainloop
    pyglet.app.run()
