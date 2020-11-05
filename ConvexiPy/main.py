import csv
import os

import cv2 as cv
import numpy as np

import convexity as conv
from convexcropper import ConvexCropper
from croppertk import Cropper

imgexts = ['jpg', 'tif', 'png', 'bmp']

# creates UI object from which file is selected and crops are perfroemd
root = ConvexCropper()
root.mainloop()

# directory where output images are stored
crops = os.listdir(root.newdir)

# get name of csv file to be generated
csvname = root.og_filename + '_conv.csv'

with open(csvname, 'w', newline='') as csvfile:
    w2csv = csv.writer(csvfile, delimiter=',',
                       quotechar='|', quoting=csv.QUOTE_MINIMAL)
    w2csv.writerow(['filename', 'convexity', 'aggregate area', 'convex area'])

    for file in crops:
        if any(file.endswith(x) for x in imgexts):
            # read image from dir
            img = cv.imread(os.path.join(root.newdir, file), 0)

            # thresh = nd array of binary image, ret is not used
            ret, thresh = cv.threshold(img, 127, 255, cv.THRESH_BINARY)

            # write binarized image to disk
            f, e = os.path.splitext(str(file))
            filename = f + '_bin' + e
            filepath = os.path.join(root.newdir, filename)
            cv.imwrite(filepath, thresh)

            if not conv.disableMATLABcomponents:
                # write stats to csv
                agg_area = conv.ptCount(thresh)  # aggregate area
                print("projected area: ", agg_area)
                conv_area = conv.convMATLAB(thresh)  # convex hull area
                print("convex area: ", conv_area)
                w2csv.writerow(
                    [filename, agg_area/conv_area, agg_area, conv_area])
