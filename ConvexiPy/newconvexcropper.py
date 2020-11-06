#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
roughly based on cropper-tk
'''
import os
import sys
import tkinter as tk
from pathlib import Path
from tkinter import filedialog as tkfd

from PIL import Image, ImageChops, ImageFilter, ImageTk

from rect import Rect

PROGNAME = 'Cropper-Tk'
VERSION = '0.20200509'

thumbsize = 896, 608
thumboffset = 16


class CropperMenuBar(tk.Menu):
    def __init__(self, master):
        self.menubar = tk.Menu(self)

    def create_filemenu(self):
        pass

    def create_editmenu(self):
        pass

    def create_aboutmenu(self):
        pass

    def create_guidemenu(self):
        pass

    def create_toolsmenu(self):
        pass


class Cropper(tk.Tk, CropperMenuBar):

    def __init__(self, master=None):
        tk.Tk.__init__(self, master)
        self.grid()
        self.initCanvas()

        # holds separate menu frames
        self.container = tk.Frame(self)
        self._frame = None

        self.init_base_frame()

        self.original_img = None
        self.edited_img = None

        '''create menu bar'''
        self.init_menu_bar()
        self.config(menu=self.menubar)

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

    '''window initiators'''

    def init_menu_bar(self):
        self.menubar = tk.Menu(master=self)
        self.create_filemenu(menubar=self.menubar)

    def init_canvas(self, image):
        pass

    def switch_frame(self, frameobj, *args, **kwargs):
        # idk if kwargs will pass its items or itself
        new_frame = frameobj(self, **kwargs)
        if self._frame is not None:
            self._frame.destroy()
        self._frame = new_frame
        self._frame.pack()

    '''utility functions'''

    def getFile(self):  # should return image
        self.file = tkfd.askopenfile(mode='rb', filetypes=[
            ('Image Files', '.jpg .JPG .jpeg .JPEG .png .PNG .tif .TIF .tiff .TIFF'),
            ('TIFF Image Files', '.tif .TIF .tiff .TIFF')
        ])
        self.image = Image.open(self.file)
        self.filename = self.file.name

        # need to redraw canvas and wipe stored crop metadata

    def saveImage(self, image):
        if image is not None:
            filename = tkfd.asksaveasfilename()
            file = open(image, mode='a')
            file.write(filename)
            file.close()
        else:
            raise FileNotFoundError

    def saveOG(self):
        saveImage(self.original_img)

    def saveED(self):
        saveImage(self.edited_img)

    '''Menu stuff'''

    def create_filemenu(self, menubar):
        filemenu = tk.Menu(master=menubar, tearoff=0)
        filemenu.add_command(label="Open", command=self.getFile)
        filemenu.add_command(label="Save original image", command=self.saveOG)
        filemenu.add_command(label="Save edited image", command=self.saveED)
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

        self.toolButtons = tk.LabelFrame(self._frame, text='Utilities')
        self.binarizeButton = tk.Button(
            master=self.toolButtons, text='BW', command=dummy)
        self.drawButton = tk.Button(
            master=self.toolButtons, text='Draw', command=dummy)

        self._frame.grid()
        self.toolButtons.grid(row=0, column=0)

        self.drawButton.grid(row=0, column=0)
        self.binarizeButton.grid(row=0, column=1)

    def init_draw_frame(self):
        '''draw stuff'''
        self.first_menu_step()

    def init_bw_frame(self):
        self.first_menu_step()

    def init_basic_menu(self):
        self.basicButtons = tk.LabelFrame(self._frame, text='Basics')

        self.cropsButton = tk.Button(self.basicButtons, text='Crop')
        self.resetButton = tk.Button(self.basicButtons, text='Reset')
        self.undoButton = tk.Button(self.basicButtons, text='Undo')
        self.exitButton = tk.Button(
            self.basicButtons, text='Exit', command=self.quit)

        self.basicButtons.grid(row=0, column=1, padx=50)
        self.cropsButton.grid(row=0, column=0)
        self.resetButton.grid(row=0, column=1)
        self.undoButton.grid(row=0, column=2)
        self.exitButton.grid(row=0, column=4)


def dummy():
    print('dummy')


def main():
    root = Cropper()
    root.mainloop()


if __name__ == '__main__':
    main()
