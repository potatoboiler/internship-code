import csv
import os

import cv2 as cv
import numpy as np
from matplotlib import pyplot as plt

import convexity as conv
from croppertk import Cropper

imgexts = ['jpg', 'tif', 'png', 'bmp']

root = Cropper()
root.mainloop()
crops = os.listdir(root.newdir)

csvname = root.og_filename + '_conv.csv'

with open(csvname, 'w', newline='') as csvfile:
    w2csv = csv.writer(csvfile, delimiter=',',
                       quotechar='|', quoting=csv.QUOTE_MINIMAL)
    w2csv.writerow(['filename', 'convexity', 'aggregate area', 'convex area'])

    for file in crops:
        if any(file.endswith(x) for x in imgexts):
            # read image from dir
            img = cv.imread(os.path.join(root.newdir, file), 0)
            ret, thresh = cv.threshold(img, 127, 255, cv.THRESH_BINARY)

            # write binary image to disk
            f, e = os.path.splitext(str(file))
            filename = f + '_bin' + e
            #print('FILENAME ', filename)
            filepath = os.path.join(root.newdir, filename)
            cv.imwrite(filepath, thresh)
            # thresh = nd array of binary image

            # print(thresh)
            # write stats to csv
            agg_area = conv.ptCount(thresh)
            print("projected area: ", agg_area)
            conv_area = conv.convMATLAB(thresh)
            print("convex area: ", conv_area)

            w2csv.writerow([filename, agg_area/conv_area, agg_area, conv_area])
