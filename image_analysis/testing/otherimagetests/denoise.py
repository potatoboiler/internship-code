import cv2
import numpy as np
import matplotlib.pyplot as plt

img = cv2.imread('C:/Users/Laurence/Documents/GitHub/internship-code/testing/testingforcontour.jpg')
print(type(img))

'''
for i in range(10, 50, 10):
    dst = cv2.fastNlMeansDenoising(img, None, i, 7, 21)
    cv2.imwrite("C:/Users/Laurence/Documents/GitHub/internship-code/testing/testimage_h=" + str(i) + '.jpg', dst)
'''

#blur = cv2.bilateralFilter(img, 9, 75, 75)

# cv2.imshow('name',blur)

# cv2.imwrite('C:/Users/Laurence/Documents/GitHub/internship-code/testing/name4.jpg',blur)
black = np.zeros_like(img, dtype=np.float32)
imgray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
ret, thresh = cv2.threshold(
    imgray,
    thresh=127,
    maxval=255,
    type=0
)
cv2.imshow('bac', imgray)
contours, hierarchy = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)
cv2.drawContours(black, contours, 0, (0, 0, 255), 1)

cv2.imshow('black', black)
cv2.waitKey(0)
