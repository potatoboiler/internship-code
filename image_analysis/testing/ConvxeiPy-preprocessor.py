
import tkinter
from tkinter.filedialog import askopenfilename

import cv2 as cv
import matplotlib.pyplot as plt
import numpy as np
from matplotlib import pyplot as plt
from matplotlib.widgets import Button, RadioButtons, Slider
from PIL import Image, ImageOps
from scipy import ndimage as ndi
from skimage import color
from skimage.exposure import histogram
from skimage.filters import sobel
from skimage.segmentation import watershed

#newmask = cv.imread('C:/Users/Laurence/Documents/GitHub/internship-code/testing/test4mask2.jpg',0)
img = cv.imread('C:/Users/Laurence/Documents/GitHub/internship-code/Images/t.tif')
print(img.shape)
mask = np.zeros(img.shape[:2],np.uint8)
#mask[newmask == 0] = 0
#mask[newmask == 255] = 1


bgdModel = np.zeros((1,65),np.float64)
fgdModel = np.zeros((1,65),np.float64)
rect = (0,0,img.shape[0], img.shape[1])

cv.grabCut(img,mask,rect,bgdModel,fgdModel,5,cv.GC_INIT_WITH_RECT)
mask = np.where((mask==2)|(mask==0),0,1).astype('uint8')
img = img*mask[:,:,np.newaxis]
plt.imshow(img),plt.colorbar(),plt.show()

"""
NOTES:

can definitely use grab cut on smaller images, without fibers
use cropper tk to find rects, then do that
mask them onto a black array
use minimal manual intervnetion

"""