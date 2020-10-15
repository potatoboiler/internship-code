import os

import cv2 as cv
import numpy as np
from scipy import spatial
from matplotlib import pyplot as plt
from PIL import Image


def load_image(infilename) -> np.ndarray:
    img = Image.open(infilename)
    img.load()
    data = np.asarray(img, dtype="int32")
    return data


def arr2Pts(arr: np.ndarray):
    out = []
    for i in range(len(arr)):
        for j in range(len(arr[0])):
            if arr[i][j] > 0:
                out.append((i, j))
    return out


def ptCount(p: np.ndarray) -> int:
    """
    to be used on raw binary image array
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


def convexArea(binimg: np.ndarray) -> int:
    # print(arr2Pts(binimg))
    convhull = spatial.ConvexHull(spatial.ConvexHull(np.array(arr2Pts(binimg))).points)

    print((convhull.points), "len ")
    convarea = area(convhull.points)

    fig = plt.figure()
    ax = fig.add_subplot(1, 1, 1)
    for visible_facet in convhull.simplices[convhull.good]:
        ax.plot(convhull.points[visible_facet, 0],
                convhull.points[visible_facet, 1],
                color='violet',
                lw=6)
    spatial.convex_hull_plot_2d(convhull, ax=ax)
    plt.show()
    return convarea
