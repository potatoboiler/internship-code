"""
A few notes:
Most of the ideas for the crop.py tool were taken from the cropper-tk library, found here:
https://github.com/ImageProcessing-ElectronicPublications/python-cropper-tk

If you try cropping an image of the same filename as one you've already cropped, that will results in undefined behavior and potentially exponential duplication of image files. Please try to delete previous files if you need to re-crop something.

The 'Zooming' frame doesn't have any functionality for this tool, and can be overriden.
"""
import csv
import os
import tkinter as tk
import platform

import cv2 as cv
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageTk

import convexity as conv
from croppertk import Cropper
from rect import Rect

font = None
if platform.system() == 'Darwin':
    font = ImageFont.truetype("/Library/Fonts/Arial Unicode.ttf", size=26)
else:
    font = ImageFont.truetype("arial.ttf", size=26)
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

        # will be used to store values for cropped region properties, but is not currently implemented
        # consolidating everything into these variables will stop double computation, but I have not gone through this yet
        # stores variables as list {key: (image, (coordinates), (aggregate area, convex area, convexity))}
        self.cropped_bits = []

        # various rectangles
        self.canvas_rects = []  # drawn rects on image
        self.crop_rects = []  # crop areas
        self.region_rect = []  # zoom windows
        self.current_rect = None

        # just some mode trackers
        # these can be removed at some point because they are hardly being used
        self.zoommode = False  # ??
        self.countour = False  # ??
        self.acbwmode = False  # black/white
        self.zooming = False  # ??

        # checks if substrate is presnet
        self.substrate = False

        # properties used for cropping
        # these variables aren't being used for any functionality, but removing these will break stuff
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
        ''' Begins the cropping purpose'''
        cropcount = 0

        # used for writing text onto image
        self.draw = ImageDraw.Draw(self.image)

        # og_filename i think is the base of the name of the original file
        self.og_filename = os.path.splitext(self.filename.split('/')[-1])[0]
        self.extension = os.path.splitext(self.filename.split('/')[-1])[-1]
        # print(self.extension, '   extension')

        # path to directory of output for the loaded image
        # takes the CURRENT WORKING DIRECTORY (i.e. the directory from which script is run from (NOT NECESSARILY THE SAME AS THE LOCATION OF THE SCRIPT)*) and creates an output folder there, storing all outputs from this script there
        # for example, current working directory works the same as you expect if you run through command line.
        # Otherwise, a common working directory might be C:\Users\<username> on Windows, or the Home folder on MacOS.
        # If on Linux, this may be the ~/ directory
        self.newdir = os.path.join(
            os.getcwd() + os.sep + 'output' + os.sep + 'crops_' + self.og_filename + os.sep
        )
        try:
            os.makedirs(self.newdir)
        except:
            pass

        # template string for creating files with the filename of the original image
        self.writedir = os.path.join(self.newdir + self.og_filename)

        for croparea in self.crop_rects:
            cropcount += 1
            f = self.newfilename(cropcount)
            # print(f, croparea)
            self.crop(croparea, f)

        # write image
        self.image.save(os.path.join(
            self.newdir + os.sep + 'convex_' + self.og_filename + self.extension))

        self.output()  # writes all the images and computes data and stuff
        try:
            os.remove('temp' + self.extension)
        except:
            print('lol')

        # Once computation is done, prints this affirmative dialog box
        exitmsg = tk.Tk()
        exitmsg.grid()

        exitlabel = tk.Label(
            master=exitmsg, text="Done! You may exit now", padx=50, pady=50)
        exitlabel.grid()

    # Overrides utilButtons() from cropper-tk
    def utilButtons(self):
        super().utilButtons()
        # reuse countourbutton, which is useless
        self.countourButton.config(
            text="Substrate?",
            command=self.substrateButton
        )

    def substrateButton(self):
        if self.substrate:
            self.substrate = False
        else:
            self.substrate = True

    def displayimage(self):
        ''' Creates a copy of the loaded image, and crops the copy, to display onto the canvas. The original image is preserved. The size parameters thumbsize may be changed through the thumbsize tuple at the top of the file. '''
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
        ''' Given a region of the original image and a filename, generates image crop from original '''
        # save crop
        ca = (croparea.left, croparea.top, croparea.right, croparea.bottom)
        newimg = self.image.crop(ca)
        newimg.save(filename)

        # binarizes image yet again, but this step is only necessary if this tool is run standalone
        ret, thresh = cv.threshold(
            cv.imread(filename, 0), 127, 255, cv.THRESH_BINARY)

        # need to write to a dictionary attached to self with { key: filename } as pairs
        # computes convexity and writes it onto original image
        convexity = conv.ptCount(thresh) / conv.convPython(thresh)[0]

        self.draw.text((croparea.left, croparea.top),
                       text=str(round(convexity, ndigits=4)),
                       fill=(255, 255, 255),
                       font=font)

    def output(self):
        ''' Given all the crop regions, computes all data and generates appropriate cropped images and outputs data to csv file. '''
        # creates UI object from which file is selected and crops are perfroemd
        # move images to memory, then process them there and save after

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
                if any(s in file for s in ["_bin.", ".csv", "convex-"]):
                    continue
                # read image from dir
                img = cv.imread(os.path.join(self.newdir, file), 0)

                # thresh = numpy array of binary image, ret is not used
                ret, thresh = cv.threshold(img, 127, 255, cv.THRESH_BINARY)

                # write binarized image to disk
                f, e = os.path.splitext(str(file))
                filename = f + '_bin' + e
                filepath = os.path.join(self.newdir, filename)
                if __name__ == '__main__':
                    cv.imwrite(filepath, thresh)

                # write stats to csv
                agg_area = conv.ptCount(thresh)  # aggregate area
                print("projected area: ", agg_area)
                conv_area = conv.convPython(thresh)[0]  # convex hull area
                print("convex area: ", conv_area)
                w2csv.writerow(
                    [filename, agg_area/conv_area, agg_area, conv_area])


if __name__ == '__main__':

    # creates UI object from which file is selected and crops are perfroemd
    root = ConvexCropper()
    root.mainloop()
