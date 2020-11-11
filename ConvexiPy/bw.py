'''
roughly based on cropper-tk
'''
import os
import tkinter as tk
from tkinter import filedialog as tkfd

import cv2 as cv
import numpy as np
from PIL import Image, ImageTk

from rect import Rect

thumbsize = 896, 608
thumboffset = 16
frameoffset = 10


class BW(tk.Tk):

    def __init__(self, master=None, image=None, filename=None):
        tk.Tk.__init__(self, master)
        self.grid()
        self.initCanvas()

        if __name__ == '__main__' or image is None:
            self.getFile()
        else:
            self.image = image.copy()
            self.filename = filename
        self.loadimage()

        self.bw_thresh = 127

        # holds separate menu frames
        self._frame = None
        self.init_base_frame()

        self.edited_img = None

        '''create menu bar'''
        self.init_menu_bar()
        self.config(menu=self.menubar)

        # properties used for cropping
        self.w = 1
        self.h = 1
        self.x0 = 0
        self.y0 = 0
        self.n = 0

    '''window initiators'''

    def init_menu_bar(self):
        self.menubar = tk.Menu(master=self)
        self.create_filemenu(menubar=self.menubar)

    def initCanvas(self):
        self.canvas = tk.Canvas(self, height=1, width=1, relief=tk.SUNKEN)
        self.canvas.grid()
        self.editedCanvas = None

    '''utility functions'''

    def extension(self):
        # print(self.filename)
        e = os.path.splitext(self.filename)[1]
        return e

    def saveImage(self, image):
        if image is not None:
            filename = tkfd.asksaveasfilename(filetypes=[(
                'Image Files', '.jpg .JPG .jpeg .JPEG .png .PNG .tif .TIF .tiff .TIFF'), ('TIFF Image Files', '.tif .TIF .tiff .TIFF')])
            filename += self.extension()
            self.edited_img.save(filename)
        else:
            raise FileNotFoundError

    def saveED(self):
        self.saveImage(self.edited_img)

    '''Menu stuff'''

    def create_filemenu(self, menubar):
        filemenu = tk.Menu(master=menubar, tearoff=0)
        #filemenu.add_command(label="Open", command=self.getFile)
        filemenu.add_command(label="Save black/white", command=self.saveED)
        filemenu.add_separator()
        filemenu.add_command(label="Exit", command=self.quit)
        menubar.add_cascade(label="File", menu=filemenu)

    '''frames'''

    def first_menu_step(self):
        '''destroys current tool frame, attaches basic menu steps'''
        if self._frame is not None:
            self._frame.destroy()
        self._frame = tk.Frame(self)
        self.init_basic_menu()

    def init_base_frame(self):
        '''basic menu, created upon startup and navigates to others'''
        self.first_menu_step()

        self.bwToolsFrame = tk.LabelFrame(
            self._frame, text='Black/White tools', padx=0)
        self.bwThresholdScale = tk.Scale(
            master=self.bwToolsFrame, from_=0, to=255, orient=tk.HORIZONTAL, label='Threshold', command=self.updateBWT)
        self.bwThresholdScale.set(self.bw_thresh)

        self.bwInc = tk.Button(
            self.bwToolsFrame, text='+1', command=self.incBWT5)
        self.bwInc5 = tk.Button(
            self.bwToolsFrame, text='+5', command=self.incBWT5)
        self.bwInc10 = tk.Button(
            self.bwToolsFrame, text='+10', command=self.incBWT10)

        self.bwDec = tk.Button(
            self.bwToolsFrame, text='-1', command=self.decBWT)
        self.bwDec5 = tk.Button(
            self.bwToolsFrame, text='-5', command=self.decBWT5)
        self.bwDec10 = tk.Button(
            self.bwToolsFrame, text='-10', command=self.decBWT10)

        self._frame.grid(pady=frameoffset)
        self.bwToolsFrame.grid(row=0, column=0)

        # add these buttons back in later
        self.bwDec10.grid(row=0, column=0)
        self.bwDec5.grid(row=0, column=1)
        self.bwDec.grid(row=0, column=2)
        self.bwThresholdScale.grid(row=0, column=3)
        self.bwInc.grid(row=0, column=4)
        self.bwInc5.grid(row=0, column=5)
        self.bwInc10.grid(row=0, column=6)

    def incBWT(self):
        self.bw_thresh += 1
        self.bwThresholdScale.set(self.bw_thresh)

    def incBWT5(self):
        for i in range(5):
            self.incBWT()

    def incBWT10(self):
        for i in range(10):
            self.incBWT()

    def decBWT(self):
        self.bw_thresh -= 1
        self.bwThresholdScale.set(self.bw_thresh)

    def decBWT5(self):
        for i in range(5):
            self.decBWT()

    def decBWT10(self):
        for i in range(10):
            self.decBWT()

    def updateBWT(self, event):
        self.bw_thresh = self.bwThresholdScale.get()

        self.edited_img = Image.fromarray(cv.threshold(
            cv.cvtColor(np.array(self.image), cv.COLOR_RGB2BGR),
            thresh=self.bw_thresh,
            maxval=255,
            type=cv.THRESH_BINARY
        )[1])

        self.display_edited()

    def init_basic_menu(self):
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
                self.basicButtons, text='Next' '''initiate next stage''')

    ''' file ops '''

    def getFile(self):  # should return image
        self.file = tkfd.askopenfile(mode='rb', filetypes=[
            ('Image Files', '.jpg .JPG .jpeg .JPEG .png .PNG .tif .TIF .tiff .TIFF'),
            ('TIFF Image Files', '.tif .TIF .tiff .TIFF')
        ])
        self.image = Image.open(self.file)
        self.filename = self.file.name

        # need to redraw canvas and wipe stored crop metadata

    def loadimage(self):
        self.image_rect = Rect(self.image.size)
        self.w = self.image_rect.w
        self.h = self.image_rect.h
        self.region_rect = Rect((0, 0), (self.w, self.h))

        self.edited_img = self.image.copy().convert('RGB')

        self.displayimage()
        self.display_edited()

    def displayimage(self):  # to do: substitute all edited image operations
        self.rr = (self.region_rect.left, self.region_rect.top,
                   self.region_rect.right, self.region_rect.bottom)
        self.image_thumb = self.image.crop(self.rr)
        self.image_thumb.thumbnail(thumbsize, Image.ANTIALIAS)

        self.image_thumb_rect = Rect(self.image_thumb.size)

        self.photoimage = ImageTk.PhotoImage(self.image_thumb, master=self)
        self.img_w, self.img_h = self.image_thumb.size
        self.canvas.configure(
            width=(2*self.img_w + 3 * thumboffset),
            height=(self.img_h + 2 * thumboffset))

        self.canvas.create_image(
            thumboffset,
            thumboffset,
            anchor=tk.NW,
            image=self.photoimage)

        x_scale = float(self.region_rect.w) / self.image_thumb_rect.w
        y_scale = float(self.region_rect.h) / self.image_thumb_rect.h
        self.scale = (x_scale, y_scale)

    def display_edited(self):
        self.edited_imgTk = self.edited_img.crop(self.rr)
        self.edited_imgTk.thumbnail(thumbsize, Image.ANTIALIAS)
        self.edited_imgTk = ImageTk.PhotoImage(self.edited_imgTk, master=self)

        if self.editedCanvas is None:
            self.editedCanvas = self.canvas.create_image(
                2*thumboffset + self.img_w, thumboffset, anchor=tk.NW, image=self.edited_imgTk)
        else:
            self.canvas.itemconfig(self.editedCanvas, image=self.edited_imgTk)


if __name__ == '__main__':
    root = BW()
    root.mainloop()
