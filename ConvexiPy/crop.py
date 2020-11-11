import csv
import os
import sys
import tkinter as tk
from pathlib import Path
from tkinter import filedialog as tkfd

import cv2 as cv
from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageFont, ImageTk

import convexity as conv
from croppertk import Cropper
from rect import Rect

font = ImageFont.truetype("arial.ttf", size=26)
disableMATLABcomponents = True


class ConvexCropper(Cropper):
    def start_cropping(self):
        cropcount = 0
        # used for writing text onto image
        self.draw = ImageDraw.Draw(self.image)

        # og_filename i think is the base of the name of the original file
        self.og_filename = os.path.splitext(self.filename.split('/')[-1])[0]
        self.extension = os.path.splitext(self.filename.split('/')[-1])[-1]
        print(self.extension, '   extension')
        self.newdir = os.path.join(
            os.getcwd() + os.sep + 'crops_' + self.og_filename + os.sep)
        try:
            os.makedirs(self.newdir)
        except:
            pass

        self.writedir = os.path.join(self.newdir + self.og_filename)

        for croparea in self.crop_rects:
            cropcount += 1
            f = self.newfilename(cropcount)
            #print(f, croparea)
            self.crop(croparea, f)

        # write image
        self.image.save(os.path.join(
            os.getcwd() + os.sep + 'convex_' + self.og_filename + self.extension))

        self.quit()

    def crop(self, croparea, filename):
        # save crop
        ca = (croparea.left, croparea.top, croparea.right, croparea.bottom)
        newimg = self.image.crop(ca)
        newimg.save(filename)

        # write convexity onto file
        ret, thresh = cv.threshold(
            cv.imread(filename, 0), 127, 255, cv.THRESH_BINARY)
        
        convexity = conv.ptCount(thresh) / conv.convMATLAB(thresh)[0] if not disableMATLABcomponents else 0

        self.draw.text((croparea.left, croparea.top),
                       text=str(round(convexity, ndigits=4)),
                       fill=(255,255,255),
                       font=font)

