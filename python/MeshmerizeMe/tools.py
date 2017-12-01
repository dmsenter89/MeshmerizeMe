# -*- coding: utf-8 -*-
# tools for contours as collections of points
# or collections of Bezier curves

# ======================================================
# Some supporting functions

from scipy.spatial import KDTree
import numpy as np
import cv2


"""
cubic_smooth_bezier
-------------------
(Evaluates a Cubic bezier or one of
it's derivative at a certain point)

    - Args:
         p: coefficients for the cubic bezier, (3,) shape array like object
         t: float from 0 to 1.
         d: order of the derivative
    - Returns:
         the y coordinate for the
"""

def cubic_smooth_bezier(p, t, d = 0):
    if d == 0:
        return (1. - t)**3*p[0]  + 3.*(1. - t)**2*t*p[0] + 3*(1. - t)*t**2*p[1] + t**3*p[2]
    elif d == 1:
        return 6.*(1. - t)*t*(p[1] - p[0]) + 3.*t**2*(p[2] - p[1])
    elif d == 2:
        return 6.*(1. - t)*(p[1] - 2.*p[0] + p[0]) + 6.*t*(p[2] - 2.*p[1] + p[0])

"""
brightness
-----------
Gets the average brightness of an image at an array of points along certain vectors
for the purpose of getting the inner / outer direction of a contour

    - Args:
         dd: (N,2) array of normalized vector directions
         out: (N,2) array of positions
         imgray: a 2d array of gray-scale pixel values
    - Returns:
         average pixel values 5 pixels out in the directions specified
""" 
def brightness(dd, out, imgray):
    out[np.where((out[:,0].astype(np.int32) > imgray.shape[1] - 1) | (out[:,1].astype(np.int32) > imgray.shape[0] - 1))] = np.zeros(2)
    
    vals = np.array([imgray[int(np.floor(uv[1])) - 1, int(np.floor(uv[0])) - 1] for uv in out], dtype = np.float32)

    maxx = np.max(out[:,0])
    maxy = np.max(out[:,1])
    minx = np.min(out[:,0])
    miny = np.min(out[:,1])
    
    counts = np.zeros(vals.shape)

    for dp in np.linspace(0.1, 5., 6):
        to_move = dd*dp
        nout = to_move + out

        i = np.where((nout[:,0].astype(np.int32) > imgray.shape[1] - 1) | (nout[:,1].astype(np.int32) > imgray.shape[0] - 1))
        nout[i] = np.array([np.nan, np.nan])
        _ = np.zeros(vals.shape)
        _[list(set(range(len(vals))).difference(i[0]))] = np.array([imgray[int(uv[1]), int(uv[0])] for uv in nout if not np.isnan(uv[0])])

        #print _
        counts[np.where((nout[:,0].astype(np.int32) < imgray.shape[1] - 1) | (nout[:,1].astype(np.int32) < imgray.shape[0] - 1))] += 1.
        
        vals += _.astype(np.float32)

    i = np.where(counts != 0.)
    vals[i] = vals[i] / counts
    vals[np.where((out[:,0] < minx + 10) | (out[:,1] > maxx - 5))] = np.nan
    
    return vals

def get_rets(contours, pt):
    rets = []
    for c in contours:
        _ = cv2.pointPolygonTest(c, tuple(pt), False)
        if _ == 1:
            rets.append(True)
        else:
            rets.append(False)

    return rets
"""
get_diameters
----------------
Attempts to estimate the diameters inside a contour.

    - Args:
        beziers: list of coefficients for cubic bezier curves that make up a contour
        mask: masked image for the distinction between inner and out directions

    - Returns:
        dictionary of diameters and their corresponding x and y coordinates of the midpoints
        
"""
def get_diameters(contours, beziers, mask):
    nvs = []
    xys = []
    diameters = []

    dataf = dict()
    dataf['diameter'] = list()
    dataf['x_midpoint'] = list()
    dataf['y_midpoint'] = list()

    imgray = mask
    
    dd = []
    _ = []
    
    for b in beziers:
        _.append(cubic_smooth_bezier(b, 0.5))
        v = cubic_smooth_bezier(b, 0.5, d = 1)
        dd.append([-v[1], v[0]])
            
    dd = np.array(dd)
    norm = np.sqrt(np.sum(np.power(dd, 2), axis = 1))

    # both directions
    dd = dd / np.hstack((np.reshape(norm, (len(norm), 1)), np.reshape(norm, (len(norm), 1))))
    ndd = -dd

    vals1 = brightness(dd, np.array(_), imgray)
    vals2 = brightness(ndd, np.array(_), imgray)

    vals = np.vstack((vals1, vals2))
    indices = np.where((np.isnan(vals1) == False) & (np.isnan(vals1) == False))[0]
            
    maxs = np.nanargmax(vals[:,indices], axis = 0)

    for i in range(len(indices)):
    
        if maxs[i] == 0:
            nvs.append(dd[indices[i]])
        else:
            nvs.append(ndd[indices[i]])
        xys.append(_[indices[i]])

        
    nvs = np.array(nvs)
    xys = np.array(xys)

    mouts = contours[0]

    for i in range(1, len(contours)):
        mouts = np.vstack((mouts, contours[i]))

    mouts = mouts.reshape((len(mouts), 2)) 

    si = []
            
    #print len(tcks)
    for i in range(len(nvs)):
        nv = nvs[i]
        xy = xys[i]
        #print xy
        xy = np.tile(xy, (len(mouts), 1))

        dirs = mouts - xy
        norm = np.sqrt(np.sum(np.power(dirs, 2), axis = 1))

        dirs = dirs / np.hstack((np.reshape(norm, (len(norm), 1)), np.reshape(norm, (len(norm), 1))))
        
        _ = np.tile(nv, (len(mouts), 1))
        dots = np.sum(dirs*_, axis = 1)
        dots = np.arccos(dots)

        eligible = mouts[np.where((dots < np.pi*(3. / 180.)))[0]]
        eligible = eligible.astype(np.float32)
        
        if eligible.shape[0] != 0:
            tree = KDTree(eligible)

            d, index = tree.query(xy[0])
            diameters.append(d)
            #print d
            si.append(i)

    for k in si:
        x1, y1 = xys[k]
        x2, y2 = xys[k] + nvs[k]*diameters[si.index(k)]
        xm, ym = xys[k] + nvs[k]*diameters[si.index(k)]*0.5

        rets = get_rets(contours, np.array([xm,ym]))

        if True in rets:
            dataf['diameter'].append(diameters[si.index(k)])
            dataf['x_midpoint'].append(xm)
            dataf['y_midpoint'].append(ym)

    return dataf, xys, diameters, nvs, si


    
            
