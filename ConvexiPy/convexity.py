import os

import cv2 as cv
import matlab
import matlab.engine
import numpy as np
from matplotlib import pyplot as plt
from PIL import Image
from scipy import spatial

eng = matlab.engine.start_matlab()



def load_image(infilename) -> np.ndarray:
    """
    load image into numpy array
    """
    img = Image.open(infilename)
    img.load()
    data = np.asarray(img, dtype="int32")
    return data


def arr2Pts(arr: np.ndarray):
    """
    convert a matrix of binary pixels to a list of coordinates
    """
    out = []
    for i in range(len(arr)):
        for j in range(len(arr[0])):
            if arr[i][j] > 0:
                out.append((i, j))
    return out


def ptCount(p: np.ndarray) -> int:
    """
    count the number of filled points in a matrix of binary pixels
    """
    area = 0
    for i in range(len(p)):
        for j in range(len(p[0])):
            if p[i][j] > 0:
                area += 1
    return area


def area(p) -> float:
    """
    Takes in list of coordinates to spit out area, use with convex hull list
    Green's theorem, as implemented here https://stackoverflow.com/questions/451426/how-do-i-calculate-the-area-of-a-2d-polygon
    """
    return 0.5 * abs(sum(x0*y1 - x1*y0 for ((x0, y0), (x1, y1)) in segments(p)))


def segments(p):  #
    """
    Takes in list of coordinates, wraps around first coord to last
    https://stackoverflow.com/questions/451426/how-do-i-calculate-the-area-of-a-2d-polygon
    """
    return zip(p, p[1:] + [p[0]])


def convMATLAB(binimg: np.ndarray):
    """
    Calls MATLAB script to compute the convex hull and area
    Argument of computeconvex is numpy matrix of pixels converted to a MATLAB array
    """
    return eng.computeconvex(matlab.uint16(np.ndarray.tolist(binimg)))


def convexArea(binimg: np.ndarray) -> int:
    """
    DO NOT USE: Uses Python scipy and numpy arrays and functions to compute area of convex hull
    """

    convhull = spatial.ConvexHull(spatial.ConvexHull(np.array(arr2Pts(binimg))).points)
    convarea = area(convhull.points)

    """ # plots the convex hull 
    fig = plt.figure()
    ax = fig.add_subplot(1, 1, 1)
    for visible_facet in convhull.simplices[convhull.good]:
        ax.plot(convhull.points[visible_facet, 0],
                convhull.points[visible_facet, 1],
                color='violet',
                lw=6)
    spatial.convex_hull_plot_2d(convhull, ax=ax)
    plt.show()
    """
    return convarea
