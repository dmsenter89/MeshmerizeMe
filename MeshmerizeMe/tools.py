# -*- coding: utf-8 -*-
# tools for contours as collections of points
# or collections of Bezier curves

# ======================================================
# Some supporting functions


from scipy.spatial import KDTree
import numpy as np
import cv2
import scipy.ndimage as nd
import matplotlib.pyplot as plt
from . import meshmerizeme_logger as logger

eps = np.finfo(float).eps

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

def dotproduct(v1, v2):
    return sum((a*b) for a, b in zip(v1, v2))


def brightness_v2(dd, out, sobelx, sobely):
    ret = []

    for i in range(len(out)):
        u, v = np.round(out[i]).astype(np.int32)

        if 0 < u <= sobelx.shape[1] and 0 < v <= sobelx.shape[0]:
            grad = np.array([sobelx[v, u], sobely[v, u]])
            grad /= np.linalg.norm(grad)

            ret.append(np.arccos(dotproduct(dd[i], grad)))
            #print ret[-1]
        else:
            ret.append(np.nan)

    return np.array(ret)

"""
Contours object
----------------
Used to save the output from ContourizeMe.  Contains the points used to construct the SVG file of cubic splines.  Can re-smooth, re-save,
or compute some metrics based on the contours.


    - Args:
        self.uv: a list of arrays of
"""
class Contours(object):
    def __init__(self, uv, beziers, info = None, uv_smoothed = None):
        self.uv = uv
        self.beziers = beziers
        self.uv_smoothed = uv_smoothed
        self.info = info

        self.im = None

    def __str__(self):
        if self.info is not None:
            return str(self.info)
        else:
            return 'Emtpy Contours object or the information dictionary has not yet been defined'

    def smooth(self, method = 'Chanvese', **args):
        ret = []

        if method == 'Chanvese':
            if self.im is None:
                self.im = cv2.imread(self.info['Image location'])

            mask = np.zeros(self.im.shape[:2])
            cv2.drawContours(mask, self.uv, -1, color = 1., thickness = -1)

            c = Chanvese()
            seg, phi, its = c.chanvese(self.im, mask, alpha = args['alpha'], max_its = args['max_its'], display = False, thresh = args['pixel_error_tolerance'])

            cs = plt.contour(phi, 0)
            for collection in cs.collections:
                paths = collection.get_paths()
                for path in paths:
                    ret.append(path.vertices)
            plt.close()

            return ret

    def perimeter(self, index = 0):
        return cv2.arcLength(np.round(self.uv_smoothed[index].reshape(len(self.uv_smoothed[index]), 1, 2)).astype(np.int32), True)
        
    def area(self, index = 0):
        return cv2.contourArea(np.round(self.uv_smoothed[index].reshape(len(self.uv_smoothed[index]), 1, 2)).astype(np.int32))

    def convex_hull(self, index = 0):
        return cv2.convexHull(np.round(self.uv_smoothed[index].reshape(len(self.uv_smoothed[index]), 1, 2)).astype(np.int32))

    def bounding_rectangle(self, index = 0):
        return cv2.boundingRect(np.round(self.uv_smoothed[index].reshape(len(self.uv_smoothed[index]), 1, 2)).astype(np.int32))

    def estimate_diameters(self, acc_bound = 100, radian_err = 3.5 * (np.pi/180.), ksize = 5):
        if self.im is None:
            self.im = cv2.imread(self.info['Image location'])

        mask = np.zeros(self.im.shape[:2])
        cv2.drawContours(mask, self.uv, -1, color = 1., thickness = -1)

        dataf, xys, diameters, nvs, si = get_diameters(self.uv_smoothed, self.beziers, mask, acc_bound = 100, radian_err = radian_err, ksize = 5)

        return xys, diameters

    def visualize(self, image = None, color = (0, 255, 0), thickness = 2):
        if image is None:
            if self.im is None:
                im = self.im = cv2.imread(self.info['Image location'])
            else:
                im = self.im

        else:
            im = image

        cv2.drawContours(im, contours, -1, color = color, thickness = thickness)
        plt.imshow(cv2.cvtColor(im, cv2.COLOR_BGR2RGB))
        plt.show()
            

    

    
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
    out[np.where((out[:, 0].astype(np.int32) > imgray.shape[1] - 1) | (out[:, 1].astype(np.int32) > imgray.shape[0] - 1))] = np.zeros(2)
    
    vals = np.array([imgray[int(np.floor(uv[1])) - 1, int(np.floor(uv[0])) - 1] for uv in out], dtype = np.float32)

    maxx = np.max(out[:, 0])
    maxy = np.max(out[:, 1])
    minx = np.min(out[:, 0])
    miny = np.min(out[:, 1])
    
    counts = np.zeros(vals.shape)

    for dp in np.linspace(0.1, 5., 6):
        to_move = dd*dp
        nout = to_move + out

        i = np.where((nout[:, 0].astype(np.int32) > imgray.shape[1] - 1) | (nout[:, 1].astype(np.int32) > imgray.shape[0] - 1))
        nout[i] = np.array([np.nan, np.nan])
        _ = np.zeros(vals.shape)
        _[list(set(range(len(vals))).difference(i[0]))] = np.array([imgray[int(uv[1]), int(uv[0])] for uv in nout if not np.isnan(uv[0])])

        #print _
        counts[np.where((nout[:, 0].astype(np.int32) < imgray.shape[1] - 1) | (nout[:, 1].astype(np.int32) < imgray.shape[0] - 1))] += 1.
        
        vals += _.astype(np.float32)

    i = np.where(counts != 0.)
    vals[i] = vals[i] / counts
    vals[np.where((out[:, 0] < minx + 10) | (out[:, 1] > maxx - 5))] = np.nan
    
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
def get_diameters(contours, beziers, mask, acc_bound = 100, radian_err = 7.5 * (np.pi/180.), ksize = 5):
    # normal vectors (normal from the the contour at a given point)
    nvs = []

    # starting point of the normal vector
    xys = []

    # list of diameters obtained
    diameters = []

    # dictionary for the storage of results
    dataf = dict()
    dataf['diameter'] = list()
    dataf['x_midpoint'] = list()
    dataf['y_midpoint'] = list()
    dataf['x1'] = list()
    dataf['y1'] = list()
    dataf['x2'] = list()
    dataf['y2'] = list()

    # the mask that we use to compute inside / outside brightness
    imgray = mask

    dd = []
    _ = []

    accs = []
    
    for b in beziers:
        _.append(cubic_smooth_bezier(b, 0.5))
        v = cubic_smooth_bezier(b, 0.5, d = 1)
        a = cubic_smooth_bezier(b, 0.5, d = 2)

        accs.append(np.linalg.norm(a))

        # get the normal vector by rotating the tangent 90 degrees
        dd.append([-v[1], v[0]])

    accs = np.array(accs)

    if acc_bound is not None:
        ix = np.where(accs < np.percentile(accs, acc_bound))
    else:
        ix = list(range(len(dd)))
            
    dd = np.array(dd)[ix]
    _ = np.array(_)[ix]
    
    norm = np.sqrt(np.sum(np.power(dd, 2), axis = 1))

    # get both directions
    dd = dd / np.hstack((np.reshape(norm, (len(norm), 1)), np.reshape(norm, (len(norm), 1))))
    ndd = -dd

    sobelx = cv2.Sobel(imgray, cv2.CV_64F, 1, 0, ksize=ksize)
    sobely = cv2.Sobel(imgray, cv2.CV_64F, 0, 1, ksize=ksize)

    # compute the brightness inside and outside 
    vals1 = brightness_v2(dd, np.array(_), sobelx, sobely)
    vals2 = brightness_v2(ndd, np.array(_), sobelx, sobely)

    vals = np.vstack((vals1, vals2))

    #print vals.shape
    #print vals
    
    indices = np.where((np.isnan(vals1) == False) & (np.isnan(vals1) == False))[0]

    #print indices
            
    maxs = np.nanargmin(vals[:, indices], axis = 0)

    # for each normal vector and it's opposite, choose the direction which points inward
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

        ix = np.where(dots < radian_err)[0]

        eligible = mouts[ix]
        eligible = eligible.astype(np.float32)

        if eligible.shape[0] != 0:
            tree = KDTree(eligible)

            d, index = tree.query(xy[0])
            diameters.append(d)

            dataf['diameter'].append(d)
            dataf['x1'].append(xy[0][0])
            dataf['y1'].append(xy[0][1])
            dataf['x2'].append(eligible[index][0])
            dataf['y2'].append(eligible[index][1])
            dataf['x_midpoint'].append((dataf['x2'][-1] + dataf['x1'][-1]) / 2.)
            dataf['y_midpoint'].append((dataf['y2'][-1] + dataf['y1'][-1]) / 2.)
            
            #print d
            si.append(i)

    return dataf, xys, diameters, nvs, si

#--------------------------
########## External code
#########################################################
"""
Should probably figure out how to point to people to the actual installation of this object, just
to be kosher.
"""
class Chanvese(object):
    def __init__(self):
        pass
    
    def chanvese(self, I, init_mask, max_its=200, alpha=0.2,
                 thresh=2, color='r', display=False):
        I = I.astype(np.float)
        print ('Chanvese smoothing...')

        # Create a signed distance map (SDF) from mask
        phi = mask2phi(init_mask)

        # Main loop
        its = 0
        stop = False
        prev_mask = init_mask
        c = 0

        ix = 0

        while (its < max_its and not stop):
            # Get the curve's narrow band
            idx = np.flatnonzero(np.logical_and(phi <= 1.2, phi >= -1.2))

            if len(idx) > 0:
                # Intermediate output
                if display:
                    if np.mod(its, 5) == 0:
                        logger.info(('iteration: {0}'.format(its)))
                        fig, axes = plt.subplots(ncols=2, figsize = (16, 8))
                        show_curve_and_phi(fig, I, phi, color)
                        ix += 1
                else:
                    if np.mod(its, 10) == 0:
                        logger.info(('iteration: {0}'.format(its)))

                # Find interior and exterior mean
                upts = np.flatnonzero(phi <= 0)  # interior points
                vpts = np.flatnonzero(phi > 0)  # exterior points
                u = np.sum(I.flat[upts]) / (len(upts) + eps)  # interior mean
                v = np.sum(I.flat[vpts]) / (len(vpts) + eps)  # exterior mean

                # Force from image information
                F = (I.flat[idx] - u)**2 - (I.flat[idx] - v)**2
                # Force from curvature penalty
                curvature = get_curvature(phi, idx)

                # Gradient descent to minimize energy
                dphidt = F / np.max(np.abs(F)) + alpha * curvature

                # Maintain the CFL condition
                dt = 0.45 / (np.max(np.abs(dphidt)) + eps)

                # Evolve the curve
                phi.flat[idx] += dt * dphidt

                # Keep SDF smooth
                phi = sussman(phi, 0.5)

                new_mask = phi <= 0
                c = convergence(prev_mask, new_mask, thresh, c)

                if c <= 5:
                    its = its + 1
                    prev_mask = new_mask
                else:
                    stop = True

            else:
                break

        # Final output
        if display:
            show_curve_and_phi(fig, I, phi, color)
            plt.savefig('levelset_end.png', bbox_inches='tight')
            pass

        # Make mask from SDF
        seg = phi <= 0  # Get mask from levelset

        return seg, phi, its


# ---------------------------------------------------------------------
# ---------------------- AUXILIARY FUNCTIONS --------------------------
# ---------------------------------------------------------------------

def bwdist(a):
    """
    Intermediary function. 'a' has only True/False vals,
    so we convert them into 0/1 values - in reverse.
    True is 0, False is 1, distance_transform_edt wants it that way.
    """
    return nd.distance_transform_edt(a == 0)

# Displays the image with curve superimposed
def show_curve_and_phi(fig, I, phi, color):
    fig.axes[0].cla()
    fig.axes[0].imshow(I, cmap='gray')
    fig.axes[0].contour(phi, 0, colors=color)
    fig.axes[0].set_axis_off()

    fig.axes[1].cla()
    fig.axes[1].imshow(phi)
    fig.axes[1].set_axis_off()
    
    plt.show()
    plt.close('all')


def im2double(a):
    a = a.astype(np.float)
    a /= np.abs(a).max()
    return a


# Converts a mask to a SDF
def mask2phi(init_a):
    phi = bwdist(init_a) - bwdist(1 - init_a) + im2double(init_a) - 0.5
    return phi


# Compute curvature along SDF
def get_curvature(phi, idx):
    dimy, dimx = phi.shape
    yx = np.array([np.unravel_index(i, phi.shape) for i in idx])  # subscripts
    y = yx[:, 0]
    x = yx[:, 1]

    # Get subscripts of neighbors
    ym1 = y - 1
    xm1 = x - 1
    yp1 = y + 1
    xp1 = x + 1

    # Bounds checking
    ym1[ym1 < 0] = 0
    xm1[xm1 < 0] = 0
    yp1[yp1 >= dimy] = dimy - 1
    xp1[xp1 >= dimx] = dimx - 1

    # Get indexes for 8 neighbors
    idup = np.ravel_multi_index((yp1, x), phi.shape)
    iddn = np.ravel_multi_index((ym1, x), phi.shape)
    idlt = np.ravel_multi_index((y, xm1), phi.shape)
    idrt = np.ravel_multi_index((y, xp1), phi.shape)
    idul = np.ravel_multi_index((yp1, xm1), phi.shape)
    idur = np.ravel_multi_index((yp1, xp1), phi.shape)
    iddl = np.ravel_multi_index((ym1, xm1), phi.shape)
    iddr = np.ravel_multi_index((ym1, xp1), phi.shape)

    # Get central derivatives of SDF at x,y
    phi_x = -phi.flat[idlt] + phi.flat[idrt]
    phi_y = -phi.flat[iddn] + phi.flat[idup]
    phi_xx = phi.flat[idlt] - 2 * phi.flat[idx] + phi.flat[idrt]
    phi_yy = phi.flat[iddn] - 2 * phi.flat[idx] + phi.flat[idup]
    phi_xy = 0.25 * (- phi.flat[iddl] - phi.flat[idur] +
                     phi.flat[iddr] + phi.flat[idul])
    phi_x2 = phi_x**2
    phi_y2 = phi_y**2

    # Compute curvature (Kappa)
    curvature = ((phi_x2 * phi_yy + phi_y2 * phi_xx - 2 * phi_x * phi_y * phi_xy) /
                 (phi_x2 + phi_y2 + eps) ** 1.5) * (phi_x2 + phi_y2) ** 0.5

    return curvature


# Level set re-initialization by the sussman method
def sussman(D, dt):
    # forward/backward differences
    a = D - np.roll(D, 1, axis=1)
    b = np.roll(D, -1, axis=1) - D
    c = D - np.roll(D, -1, axis=0)
    d = np.roll(D, 1, axis=0) - D

    a_p = np.clip(a, 0, np.inf)
    a_n = np.clip(a, -np.inf, 0)
    b_p = np.clip(b, 0, np.inf)
    b_n = np.clip(b, -np.inf, 0)
    c_p = np.clip(c, 0, np.inf)
    c_n = np.clip(c, -np.inf, 0)
    d_p = np.clip(d, 0, np.inf)
    d_n = np.clip(d, -np.inf, 0)

    a_p[a < 0] = 0
    a_n[a > 0] = 0
    b_p[b < 0] = 0
    b_n[b > 0] = 0
    c_p[c < 0] = 0
    c_n[c > 0] = 0
    d_p[d < 0] = 0
    d_n[d > 0] = 0

    dD = np.zeros_like(D)
    D_neg_ind = np.flatnonzero(D < 0)
    D_pos_ind = np.flatnonzero(D > 0)

    dD.flat[D_pos_ind] = np.sqrt(
        np.max(np.concatenate(
            ([a_p.flat[D_pos_ind]**2], [b_n.flat[D_pos_ind]**2])), axis=0) +
        np.max(np.concatenate(
            ([c_p.flat[D_pos_ind]**2], [d_n.flat[D_pos_ind]**2])), axis=0)) - 1
    dD.flat[D_neg_ind] = np.sqrt(
        np.max(np.concatenate(
            ([a_n.flat[D_neg_ind]**2], [b_p.flat[D_neg_ind]**2])), axis=0) +
        np.max(np.concatenate(
            ([c_n.flat[D_neg_ind]**2], [d_p.flat[D_neg_ind]**2])), axis=0)) - 1

    D = D - dt * sussman_sign(D) * dD
    return D


def sussman_sign(D):
    return D / np.sqrt(D**2 + 1)

# Convergence Test
def convergence(p_mask, n_mask, thresh, c):
    diff = p_mask.astype(np.float32) - n_mask.astype(np.float32)
    n_diff = np.sum(np.abs(diff))

    #print n_diff
    if n_diff < thresh:
        c = c + 1
    else:
        c = 0
    return c
    
            
