import csv
import os
import tkinter as tk

import cv2 as cv
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageTk

import convexity as conv
from croppertk import Cropper
from rect import Rect

font = ImageFont.truetype("arial.ttf", size=26)
disableMATLABcomponents = True

thumbsize = 896, 608
thumboffset = 16

imgexts = ['jpg', 'tif', 'png', 'bmp']


class ConvexCropper(Cropper):
    def __init__(self, master=None, image=None, filename=None):
        tk.Tk.__init__(self, master)
        self.initCanvas()
        self.grid()
        self.utilButtons()

        # crop area
        self.croprect_start = None
        self.croprect_end = None

        # various rectangles
        self.canvas_rects = []  # drawn rects on image
        self.crop_rects = []  # crop areas
        self.region_rect = []  # zoom windows
        self.current_rect = None

        # just some mode trackers
        self.zoommode = False  # ??
        self.countour = False  # ??
        self.acbwmode = False  # black/white
        self.zooming = False  # ??

        # properties used for cropping
        self.w = 1
        self.h = 1
        self.x0 = 0
        self.y0 = 0
        self.n = 0

        # file loading
        if __name__ == '__main__' or image is None:
            self.getFile()
        else:
            self.image = image
            self.filename = filename
        self.loadimage()

    def start_cropping(self):
        cropcount = 0
        # used for writing text onto image
        self.draw = ImageDraw.Draw(self.image)

        # og_filename i think is the base of the name of the original file
        self.og_filename = os.path.splitext(self.filename.split('/')[-1])[0]
        self.extension = os.path.splitext(self.filename.split('/')[-1])[-1]
        # print(self.extension, '   extension')
        self.newdir = os.path.join(
            os.getcwd() + os.sep + 'output' + os.sep + 'crops_' + self.og_filename + os.sep)
        try:
            os.makedirs(self.newdir)
        except:
            pass

        self.writedir = os.path.join(self.newdir + self.og_filename)

        for croparea in self.crop_rects:
            cropcount += 1
            f = self.newfilename(cropcount)
            # print(f, croparea)
            self.crop(croparea, f)

        # write image
        self.image.save(os.path.join(
            self.newdir + os.sep + 'convex_' + self.og_filename + self.extension))

        self.output()
        try:
            os.remove('temp' + self.extension)
        except:
            print('lol')

    def displayimage(self):
        rr = (self.region_rect.left, self.region_rect.top,
              self.region_rect.right, self.region_rect.bottom)
        self.image_thumb = self.image.crop(rr)

        self.image_thumb.thumbnail(thumbsize, Image.ANTIALIAS)
        if self.countour:
            self.image_thumb = self.image_thumb.filter(ImageFilter.CONTOUR)

        self.image_thumb_rect = Rect(self.image_thumb.size)

        self.photoimage = ImageTk.PhotoImage(self.image_thumb, master=self)
        w, h = self.image_thumb.size
        self.canvas.configure(
            width=(w + 2 * thumboffset),
            height=(h + 2 * thumboffset))

        self.canvas.create_image(
            thumboffset,
            thumboffset,
            anchor=tk.NW,
            image=self.photoimage)

        x_scale = float(self.region_rect.w) / self.image_thumb_rect.w
        y_scale = float(self.region_rect.h) / self.image_thumb_rect.h
        self.scale = (x_scale, y_scale)
        self.redraw_rect()
        self.set_button_state()

    def crop(self, croparea, filename):
        # save crop
        ca = (croparea.left, croparea.top, croparea.right, croparea.bottom)
        newimg = self.image.crop(ca)
        newimg.save(filename)

        # write convexity onto file
        ret, thresh = cv.threshold(
            cv.imread(filename, 0), 127, 255, cv.THRESH_BINARY)

        # write to a map attached to self with key: filename,
        convexity = np.ndarray.sum(thresh) / conv.convMATLAB(thresh)[
            0] if not disableMATLABcomponents else conv.ptCount(thresh) / conv.convPython(thresh)[0]

        self.draw.text((croparea.left, croparea.top),
                       text=str(round(convexity, ndigits=4)),
                       fill=(255, 255, 255),
                       font=font)

    def output(self):
        imgexts = ['jpg', 'tif', 'png', 'bmp']

        # creates UI object from which file is selected and crops are perfroemd

        # directory where output images are stored
        crops = os.listdir(self.newdir)

        # get name of csv file to be generated
        csvname = self.newdir + self.og_filename + '_conv.csv'

        with open(csvname, 'w', newline='') as csvfile:
            w2csv = csv.writer(csvfile, delimiter=',',
                            quotechar='|', quoting=csv.QUOTE_MINIMAL)
            w2csv.writerow(
                ['filename', 'convexity', 'aggregate area', 'convex area'])

            for file in crops:
                if any(file.endswith(x) for x in imgexts):
                    # read image from dir
                    img = cv.imread(os.path.join(self.newdir, file), 0)

                    # thresh = nd array of binary image, ret is not used
                    ret, thresh = cv.threshold(img, 127, 255, cv.THRESH_BINARY)

                    # write binarized image to disk
                    f, e = os.path.splitext(str(file))
                    filename = f + '_bin' + e
                    filepath = os.path.join(self.newdir, filename)
                    cv.imwrite(filepath, thresh)

                    # write stats to csv
                    agg_area = conv.ptCount(thresh)  # aggregate area
                    print("projected area: ", agg_area)
                    conv_area = conv.convPython(thresh)[
                        0] if conv.disableMATLABcomponents else conv.convMATLAB(thresh)[0]  # convex hull area
                    print("convex area: ", conv_area)
                    w2csv.writerow(
                        [filename, agg_area/conv_area, agg_area, conv_area])


if __name__ == '__main__':
    imgexts = ['jpg', 'tif', 'png', 'bmp']

    # creates UI object from which file is selected and crops are perfroemd
    root = ConvexCropper()
    root.mainloop()

    # directory where output images are stored
    crops = os.listdir(root.newdir)

    # get name of csv file to be generated
    csvname = root.newdir + root.og_filename + '_conv.csv'

    with open(csvname, 'w', newline='') as csvfile:
        w2csv = csv.writer(csvfile, delimiter=',',
                           quotechar='|', quoting=csv.QUOTE_MINIMAL)
        w2csv.writerow(
            ['filename', 'convexity', 'aggregate area', 'convex area'])

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
