# IMPORTANT
# https://stackoverflow.com/questions/48305991/convex-hull-in-python-for-given-set-of-points
import itertools
import cv2
import numpy as np
from skimage.morphology import convex_hull_image
from typing import List, Tuple, Union


def on(x, y, array: np.ndarray):
    array[x][y] = 255


def on(pair, array: np.ndarray):
    array[pair[0]][pair[1]] = 255


def getCoords(img: np.ndarray):
    ''' Given an image (as a numpy.ndarray), returns list of coordinates of non-off bits '''
    a = []
    x = img.shape[0]
    y = img.shape[1]

    for i in range(x):
        # print(i)
        for j in range(y):
            if any(img[i][j]):
                a.append([i, j])

    return np.array(a).astype(np.float32)


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


"""
img = np.zeros((500, 500), dtype=int).astype(np.float32)
nbits = [[100, 100], [400, 400], [300, 400], [350, 400], [375, 400], [250, 250]]
for x in onbits:
    on(x, img)
img = img.astype(np.float32)
conv = cv2.convexHull(np.array(onbits))

hull = np.array([[255 if x else 0 for x in v] for v in convex_hull_image(img)]).astype(np.uint8)

# img = np.array([[255 if x else 0 for x in v] for v in img]).astype(np.uint8)
# cv2.imshow("image", hull)
# cv2.waitKey(0)
# print(conv)
"""

#hull = np.array([[255 if any(x) else 0 for x in v] for v in convex_hull_image(binarized)]).astype(np.uint8)
#cv2.imshow("image", hull)

# cv2.waitKey(0)


def distance(p1, p2):
    return np.sqrt((p2[0]-p1[0])**2 + (p2[1] - p1[1])**2)


def maxdist(pts: List[int]):  # -> Tuple[float, np.ndarray[List[float]], np.ndarray[List[float]]]:
    ''' Gets max distance between points and returns distance, point1, and point 2 '''
    maxpts = [None, None]
    max = 0

    if len(pts.shape) == 3:
        for i in range(len(pts)):
            for j in range(i+1, len(pts)):
                dist = distance(pts[i][0], pts[j][0])
                if dist > max:
                    maxpts = [pts[i][0], pts[j][0]]
                    max = dist
    else:
        for i in range(len(pts)):
            for j in range(i+1, len(pts)):
                dist = distance(pts[i], pts[j])
                if dist > max:
                    maxpts = [pts[i], pts[j]]
                    max = dist

    return max, maxpts[0], maxpts[1]


img = cv2.imread('./testing/01-07__crop__3.tif')
black = np.zeros_like(img, dtype=np.float32)
imgray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
ret, thresh = cv2.threshold(
    imgray,
    thresh=127,
    maxval=255,
    type=0
)
#cv2.imshow('imgray', imgray)
# cv2.waitKey(0)

contours, hierarchy = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)
cv2.drawContours(black, contours, 0, (0, 0, 255), 1)
x = np.concatenate(contours)
print(cv2.convexHull(x, clockwise=False).reshape(-1, 2))
cv2.imshow('thresh', black)
# cv2.waitKey(0)

cv2.polylines(black, [cv2.convexHull(x, clockwise=False)], True, (255, 255, 255))
#cv2.imshow('thresh', black)
# cv2.waitKey(0)

max_dist = 0
max_pair = None
for pair in itertools.product(cv2.convexHull(x, clockwise=False).reshape(-1, 2), repeat=2):
    dist = np.linalg.norm(pair[0]-pair[1])
    if dist > max_dist:
        max_dist = dist
        max_pair = pair


# Roundness defined as ratio of projected particle area to area of circle with length L, where L is the maximum Feret diameter of the particle. 
# Definition taken from China et al. 2015, "Morphology of diesel soot residuals from supercooled water droplets and ice crystals: implications for optical properties"
print(max_pair)

def triangleArea(p1, p2, p3):
    return abs(p1[0]*p2[1] + p2[0]*p3[1] + p3[0] * p1[1] - (p1[1]*p2[0] + p2[1]*p3[0] + p3[1]*p1[0]))/2


def getAntipodalPairs(pts: Union[List, np.ndarray]) -> List:
    """ 
    Gets pairs of points that are "antipodal", or can be fit between two parallel planes.
    https://en.wikipedia.org/wiki/Rotating_calipers
    lol, this sucks
    """
    print(pts)
    antipodalPairs = []
    n = len(pts)
    i = 1
    j = i+1
    j0 = j

    while triangleArea(pts[i], pts[(i+1) % n], pts[(j+1) % n]) > triangleArea(pts[i], pts[(i+1) % n], pts[j]):
        j = (j+1) % n
        j0 = j
    while j != n:
        i = (i+1) % n
        antipodalPairs.append((pts[i], pts[j]))

        while triangleArea(pts[i], pts[(i+1) % n], pts[(j+1) % n]) > triangleArea(pts[i], pts[(i+1) % n], pts[j]):
            j = (j+1) % n
            if ((i, j) != (j0, n)):
                antipodalPairs.append((pts[i], pts[j]))
            else:
                return

            if triangleArea(pts[j], pts[(i+1) % n], pts[(j+1) % n]) > triangleArea(pts[i], pts[(i+1) % n], pts[j]):
                if ((i, j) != (j0, n)):
                    antipodalPairs.append((pts[i], pts[(j+1) % n]))
                else:
                    antipodalPairs.append((pts[(i+1) % n], pts[j]))

    return antipodalPairs


#print(getAntipodalPairs(cv2.convexHull(x, clockwise=False).reshape(-1, 2)))

"""

    i0 = n
    i = 1
    j = i + 1
    while (Area(i, i + 1, j + 1) > Area(i, i + 1, j))
        j = j + 1
        j0 = j
    while (j != i0)
        i = i + 1
        yield i, j
        while (Area(i, i + 1, j + 1) > Area(i, i + 1, j)
            j = j + 1
            if ((i, j) != (j0, i0))
                yield i, j
            else 
                return
        if (Area(j, i + 1, j + 1) = Area(i, i + 1, j))
            if ((i, j) != (j0, i0))
                yield i, j + 1
            else 
                yield i + 1, j
"""
