from math import sqrt

import cv2
import matplotlib.pyplot as plt
from skimage import data
from skimage.color import rgb2gray
from skimage.feature import blob_dog, blob_doh, blob_log

image = cv2.imread('C:/Users/Laurence/Documents/GitHub/internship-code/testing/testingforcontour.jpg')
image_gray = rgb2gray(image)

blur = cv2.bilateralFilter(image, 20, 75, 75)

cv2.imshow('ba', blur)
cv2.waitKey(0)
