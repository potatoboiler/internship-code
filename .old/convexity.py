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


def convMATLAB(binimg: np.ndarray):
    """
    Calls MATLAB script to compute the convex hull and area
    Argument of computeconvex is numpy matrix of pixels converted to a MATLAB array
    """
    return eng.computeconvex(matlab.uint16(np.ndarray.tolist(binimg)))


