"""
A few notes:
Most of the ideas for the crop.py tool were taken from the cropper-tk library, found here:
https://github.com/ImageProcessing-ElectronicPublications/python-cropper-tk

If you try cropping an image of the same filename as one you've already cropped, that will results in undefined behavior and potentially exponential duplication of image files. Please try to delete previous files if you need to re-crop something.

The 'Zooming' frame doesn't have any functionality for this tool, and can be overriden.

BUG: Overlapping crop regions may lead to wrong convexity values. This is because the program may write text into that crop region before it is processed by the loop. Because the text is also white, the program will detect the text as part of the shape you wish to analyze.
Workaround: DO NOT overlap crop regions.
Fix idea: load all crop regions into memory prior to processing
"""
import math
import csv
import itertools
import os
import platform
import tkinter as tk

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

    def displayExitMsg(self):
        exitmsg = tk.Tk()
        exitmsg.grid()

        exitlabel = tk.Label(
            master=exitmsg, text="Done! You may exit now", padx=50, pady=50)
        exitlabel.grid()

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

        # directory where output images are stored
        # probably can be removed, IDE gives warning about how this is not used
        crops = os.listdir(self.newdir)

        # get name of csv file to be generated
        csvname = self.newdir + self.og_filename + '_conv.csv'
        with open(csvname, 'w', newline='') as csvfile:
            w2csv = csv.writer(
                csvfile,
                delimiter=',',
                quotechar='|',
                quoting=csv.QUOTE_MINIMAL
            )
            w2csv.writerow(['filename', 'convexity', 'roundness', 'aggregate area', 'convex area'])

            # print(self.filename) #debug statement

            for croparea in self.crop_rects:
                cropcount += 1
                f = self.newfilename(cropcount)
                # print(f)

                # save crop
                ca = (croparea.left, croparea.top, croparea.right, croparea.bottom)
                newimg = self.image.crop(ca)
                newimg.save(f)

                # creates binarizes image from crop region
                ret, thresh = cv.threshold(cv.imread(f, 0), 127, 255, cv.THRESH_BINARY)

                # save generated binarized image to disk
                filename = f + '_bin' + self.extension
                filepath = os.path.join(self.newdir, filename)
                if __name__ == '__main__':
                    cv.imwrite(filepath, thresh)

                agg_area = conv.ptCount(thresh)  # aggregate area
                conv_area = conv.convPython(thresh)[0]  # convex hull area
                convexity = agg_area / conv_area
                # print("projected area: ", agg_area)
                # print("convex area: ", conv_area)

                # Find contours of particle in region
                # Note: cv.findContours manages to separate one large contour into many, for some reason
                contours, hierarchy = cv.findContours(thresh, cv.RETR_TREE, cv.CHAIN_APPROX_NONE)

                full_contour = np.concatenate(contours)
                convex_hull_vertices = cv.convexHull(points=full_contour).reshape(-1, 2)

                # Find maximum Feret diameter
                max_dist = 0
                max_pair = None  # use max_dist to draw the axis, not implemented here
                for pair in itertools.product(convex_hull_vertices, repeat=2):
                    dist = np.linalg.norm(pair[0]-pair[1])
                    if dist > max_dist:
                        max_dist = dist
                        max_pair = pair

                # L = maximum Feret diameter of particle
                # Roundness defined as ratio of area of projected particle to circle with diameter L
                # Definition taken from China et al. 2015, "Morphology of diesel soot residuals from supercooled water droplets and ice crystals: implications for optical properties"
                roundness = agg_area / (math.pi * (max_dist/2)**2)

                # Write stats to csv
                # Write a row of data to the csv file
                w2csv.writerow([filename, convexity, roundness, agg_area, conv_area])

                # writes convexity onto original image
                stats_string = 'Convexity: ' + str(round(convexity, ndigits=4)) + '\nRoundness: ' + str(round(roundness, ndigits=4))
                self.draw.text(
                    (croparea.left, croparea.top),
                    text=stats_string,
                    fill=(255, 255, 255),
                    font=font
                )

        # write image
        self.image.save(os.path.join(
            self.newdir + os.sep + 'convex_' + self.og_filename + self.extension))

        # Remove temporary storage file
        try:
            os.remove('temp' + self.extension)
        except:
            print('lol')

        # Once computation is done, prints this affirmative dialog box
        self.displayExitMsg()


if __name__ == '__main__':

    # creates UI object from which file is selected and crops are perfroemd
    root = ConvexCropper()
    root.mainloop()
