import os
import tkinter
import tkinter as tk
from tkinter import filedialog as tkfd
from tkinter.filedialog import askopenfilename

import cv2 as cv
import matplotlib.pyplot as plt
import numpy as np
from PIL import Image, ImageOps, ImageTk
from PIL.ImageChops import invert
from rect import Rect
from scipy import ndimage as ndi
from skimage import color
from skimage.exposure import histogram
from skimage.filters import sobel
from skimage.segmentation import watershed

thumbsize = 896, 608
thumboffset = 16
frameoffset = 10


class BW(tk.Tk):

    def __init__(self, master=None, image=None, filename=None):
        ''' Initializes window '''
        tk.Tk.__init__(self, master)
        self.grid()
        self.initCanvas()

        # if you are running this file directly, directly requests file
        # otherwise, copies image from the passed image parameter
        if __name__ == '__main__' or image is None:
            ''' gets file from file dialog '''
            self.file = tkfd.askopenfile(mode='rb', filetypes=[
                ('Image Files', '.jpg .JPG .jpeg .JPEG .png .PNG .tif .TIF .tiff .TIFF'),
                ('TIFF Image Files', '.tif .TIF .tiff .TIFF')
            ])
            self.image = Image.open(self.file)
            self.imageArray = np.array(ImageOps.grayscale(self.image))
            self.filename = self.file.name
        else:
            self.imageArray = np.array(ImageOps.grayscale(image))
            self.image = image.copy()
            self.filename = filename
        self.loadimage()

        # default value
        self.edited_img = np.zeros_like(self.image)
        self.thresh1 = 128
        self.thresh2 = 128

        # holds separate menu frames for holding/displaying buttons and the like
        self._frame = None
        self.init_base_frame()

        # properties used for cropping, I don't think these actually get used so these might be removable
        self.w = 1
        self.h = 1
        self.x0 = 0
        self.y0 = 0
        self.n = 0

    '''window initiators'''

    def initCanvas(self):
        ''' Initializes canvas to display loaded image, but doesn't actually display yet. Display is handled in loadimage() and displayimage() '''
        self.canvas = tk.Canvas(self, height=1, width=1, relief=tk.SUNKEN)
        self.canvas.grid()
        self.editedCanvas = None

    '''utility functions'''

    def extension(self):
        ''' Gets file's extension. May not work if file name or file path contains any dots. '''
        # print(self.filename)
        e = os.path.splitext(self.filename)[1]
        return e

    def saveImage(self, image):
        ''' Image saving functionality implemented here '''
        if image is not None:
            filename = tkfd.asksaveasfilename(filetypes=[(
                'Image Files', '.jpg .JPG .jpeg .JPEG .png .PNG .tif .TIF .tiff .TIFF'), ('TIFF Image Files', '.tif .TIF .tiff .TIFF')])
            filename += self.extension()
            self.edited_img.save(filename)
        else:
            raise FileNotFoundError

    def saveED(self):
        ''' allows one to save the edited image as a separate file '''
        self.saveImage(self.edited_img)

    def passNext(self):
        ''' Passes the current version of the edited image to the next window (i.e. from the binarization window to the drawing window) '''
        self.edited_img.save(('temp' + self.extension()))
        self.quit()

    def init_base_frame(self):
        ''' initiates menu for changing binarization threshold, created upon startup '''
        self._frame = tk.Frame(self)
        # initializes menu with basic tasks, actually that function could probably just be pasted here without any trouble
        self.init_basic_menu()

        self.bwToolsFrame = tk.LabelFrame(self._frame, text='Black/White tools', padx=0)

        self.threshold_scale1 = tk.Scale(master=self.bwToolsFrame, from_=0, to=255, orient=tk.HORIZONTAL, label='Threshold 1', command=self.updateBWT1)
        self.threshold_scale1.set(self.thresh1)

        self.threshold_scale2 = tk.Scale(master=self.bwToolsFrame, from_=0, to=255, orient=tk.HORIZONTAL, label='Threshold 2', command=self.updateBWT2)
        self.threshold_scale2.set(self.thresh2)

        self._frame.grid(pady=frameoffset)
        self.bwToolsFrame.grid(row=0, column=0)

        # add these buttons back in later
        self.threshold_scale1.grid(row=0, column=0)
        self.threshold_scale2.grid(row=1, column=0)

    def updateBWT1(self, event):
        ''' updates the displayed, binarized image (right half of the screen) '''
        self.thresh1 = int(event)

        self.edited_img = np.zeros_like(self.image)
        self.edited_img[self.imageArray < self.thresh1] = 5
        self.edited_img[self.imageArray < self.thresh2] = 255

        self.display_edited()

    def updateBWT2(self, event):
        ''' updates the displayed, binarized image (right half of the screen) '''

        self.thresh2 = int(event)

        self.edited_img = np.zeros_like(self.image)
        self.edited_img[self.imageArray < self.thresh1] = 5
        self.edited_img[self.imageArray < self.thresh2] = 255

        self.display_edited()

    def init_basic_menu(self):
        ''' initiates buttons and menu for saving, exiting, and moving to next window '''
        self.basicButtons = tk.LabelFrame(self._frame, text='Basics')

        self.saveButton = tk.Button(
            self.basicButtons, text='Save BW', command=self.saveED)

        self.basicButtons.grid(row=0, column=2, padx=10)
        self.saveButton.grid(row=0, column=0)

        if __name__ == '__main__':
            self.exitButton = tk.Button(
                self.basicButtons, text='Exit', command=self.quit)
            self.exitButton.grid(row=0, column=1)
        else:
            self.nextButton = tk.Button(
                self.basicButtons, text='Next', command=self.passNext)
            self.nextButton.grid(row=0, column=1)

    ''' file ops '''

    def loadimage(self):
        ''' loads the image file from getFile() into the GUI, placing the original image on the left half and editable version on the right '''
        self.image_rect = Rect(self.image.size)
        self.w = self.image_rect.w
        self.h = self.image_rect.h
        self.region_rect = Rect((0, 0), (self.w, self.h))

        self.edited_img = self.image.copy()

        self.displayimage()
        self.display_edited()

    def displayimage(self):  # to do: substitute all edited image operations
        ''' Creates a copy of the loaded image, and crops the copy, to display onto the canvas. The original image is preserved. The size parameters thumbsize may be changed through the thumbsize tuple at the top of the file. '''

        self.rr = (self.region_rect.left, self.region_rect.top,
                   self.region_rect.right, self.region_rect.bottom)  # stores (0, 0, width, height) where width and height are from original image
        self.image_thumb = self.image.crop(self.rr)
        self.image_thumb.thumbnail(thumbsize, Image.ANTIALIAS)

        self.image_thumb_rect = Rect(self.image_thumb.size)

        # converts cropped copy to PhotoImage object, which is the necessary type to display onto the GUI
        self.photoimage = ImageTk.PhotoImage(self.image_thumb, master=self)
        self.img_w, self.img_h = self.image_thumb.size

        # adjusts size of canvas to image size
        self.canvas.configure(
            width=(2*self.img_w + 3 * thumboffset),
            height=(self.img_h + 2 * thumboffset))

        # puts generated PhotoImage onto canvas
        self.canvas.create_image(
            thumboffset,
            thumboffset,
            anchor=tk.NW,
            image=self.photoimage
        )

        # provides scale factor between original image to cropped image
        x_scale = float(self.region_rect.w) / self.image_thumb_rect.w
        y_scale = float(self.region_rect.h) / self.image_thumb_rect.h
        self.scale = (x_scale, y_scale)

    def display_edited(self):
        ''' Displays edited image. If it doesn't already exist, then places it onto canvas the same way displayimage() does. If it does, then simply updates canvas with new image. NOT used for updating in realtime. '''
        self.edited_imgTk = self.edited_img.crop(self.rr)
        self.edited_imgTk.thumbnail(thumbsize, Image.ANTIALIAS)
        self.edited_imgTk = ImageTk.PhotoImage(self.edited_imgTk, master=self)

        if self.editedCanvas is None:
            self.editedCanvas = self.canvas.create_image(
                2*thumboffset + self.img_w, thumboffset, anchor=tk.NW, image=self.edited_imgTk)
        else:
            self.canvas.itemconfig(self.editedCanvas, image=self.edited_imgTk)


if __name__ == '__main__':  # allows user to run the tool on its own
    root = BW()
    root.mainloop()
