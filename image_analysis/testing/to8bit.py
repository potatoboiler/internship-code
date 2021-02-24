import cv2
from numpy import *

img16 = cv2.imread('./testing/testimage2.jpg')


img8 = (img16/2).astype('uint8')

cv2.imshow('3424',img8)
cv2.imwrite('C:/Users/Laurence/Documents/GitHub/internship-code/testing/name10.jpg',img8)
cv2.waitKey(0)