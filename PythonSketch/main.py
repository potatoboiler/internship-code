import os

import cv2 as cv
import numpy as np
import scipy as sp
from matplotlib import pyplot as plt

from croppertk import Cropper

imgexts = ['jpg', 'tif', 'png', 'bmp']

root = Cropper()
root.mainloop()
crops = os.listdir(root.newdir)


for file in crops:
    if any(file.endswith(x) for x in imgexts):
        # test code
        img = cv.imread(os.path.join(root.newdir, file), 0)
        ret, thresh = cv.threshold(img, 127, 255, cv.THRESH_BINARY)

        f, e = os.path.splitext(str(file))
        filename = f + '_bin' + e
        print("FILENAME ", filename)
        cv.imwrite(os.path.join(root.newdir, filename), thresh)
