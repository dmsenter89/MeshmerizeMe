# -*- coding: utf-8 -*-
# Python Class to create geometry objects for
# use with IB2D and IBAMR
# ==============================================================================
# Classes to handle the various geo_objects
#      - Vertex: the x,y grid of points. It's elements will be used as
#           as references for other objects in the plane.
#      - Spring
# ==============================================================================

class Vertex():
    """
    defines the x,y nodes in 2D
    """
    def __init__(self,x,y):
        self.x = x
        self.y = y

    def getPos(self):
        return (self.x, self.y)

    def getType(self):
        return "vertex"

    def printString(self):
        """
        Print vertex string for the .node file.
        """
        return repr(self.x) + " " + repr(self.y) + "\n" # neede to implement

class Spring():
    """
    defines a spring element.
    """
    def __init__(self,mastId,slaveId, stiff, restlen, beta):
        self.master = mastId    # master node ID
        self.slave = slaveId    # slave node ID
        self.stiff = stiff      # spring stiffness
        self.restlen = restlen  # resting length
        self.beta = beta        # deg. of nonlinearity

    def getType(self):
        return "spring"

    def printString(self):
        spring_str = repr(self.master) + " " + repr(self.slave) + \
                    " " + repr(self.stiff) + " " + repr(self.restlen) + \
                    " " + repr(self.beta) + "\n"
        return spring_str

class Beam():
    """
    defines a beam element.
    """
    def __init__(self, lID, mID, rID, stiff, curv):
        self.lID = lID
        self.mID = mID
        self.rID = rID
        self.kb = stiff     # beam stiffness
        self.c  = curv      # beam curvature

    def getType(self):
        return "beam"

    def printString(self):
        beam_str = repr(self.lID) + " " + repr(self.mID) + " " + \
                   repr(self.rID) + " " + repr(self.kb)  + " " + \
                   repr(self.c) + "\n"
        return beam_str

#===============================================================================
# Function to write the various geometry files
#===============================================================================
def writeFile(filename, geo_list):
    """
    writes the .OBJ files based on filename.
    """
    fname = filename + "." + geo_list[0].getType()
    f = open(fname, "w")
    n = len(geo_list)
    f.write(repr(n)+"\n")
    for elem in geo_list:
        f.write(elem.printString())
    f.close()

#===============================================================================
# Testing function to make sure that this file is working correctly.
#===============================================================================
def test():
    print("Beginning test.")
    v1 = Vertex(3,4)
    v2 = Vertex(5,6)
    vlist = [v1, v2]
    writeFile('test', vlist)

    s1 = Spring(3,4, 1e-4, 1.1, 4)
    s2 = Spring(5,6, 1e-4, 1.1, 4)
    slist = [s1, s2]
    writeFile('test', slist)
    print("Test completed.")

if __name__ == '__main__': test()
