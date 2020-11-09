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

import cv2 as cv
import numpy as np
from PIL import Image, ImageChops, ImageFilter, ImageTk

from rect import Rect

PROGNAME = 'Cropper-Tk'
VERSION = '0.20200509'

thumbsize = 896, 608
thumboffset = 16
frameoffset = 10


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

        self.edited_img = None
        self.undo_cache = list()

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

        # data members
        self.bw_thresh = 127

        self.getFile()
        self.loadimage()

    '''window initiators'''

    def init_menu_bar(self):
        self.menubar = tk.Menu(master=self)
        self.create_filemenu(menubar=self.menubar)

    def switch_frame(self, frameobj, *args, **kwargs):
        # idk if kwargs will pass its items or itself
        new_frame = frameobj(self, **kwargs)
        if self._frame is not None:
            self._frame.destroy()
        #self._frame = new_frame
        # self._frame.grid()

    def initCanvas(self):
        self.canvas = tk.Canvas(self, height=1, width=1, relief=tk.SUNKEN)

        # these should get moved into a frame mode
        self.canvas.bind('<Button-1>', self.canvas_mouse1_callback)
        self.canvas.bind('<ButtonRelease-1>', self.canvas_mouseup1_callback)
        self.canvas.bind('<B1-Motion>', self.canvas_mouseb1move_callback)

        self.canvas.grid()

        self.editedCanvas = None

    '''utility functions'''

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

    def canvas_mouse1_callback(self, event):
        # print(event.x, event.y)
        self.croprect_start = (event.x, event.y)
        print(event.x, ", ", event.y)

    def canvas_mouseb1move_callback(self, event):
        if self.current_rect:
            self.canvas.delete(self.current_rect)
        x1 = self.croprect_start[0]
        y1 = self.croprect_start[1]
        x2 = event.x
        y2 = event.y
        #print(x2, ", ", y2)
        bbox = (x1, y1, x2, y2)
        cr = self.canvas.create_rectangle(bbox)
        self.current_rect = cr

    def canvas_mouseup1_callback(self, event):
        self.croprect_end = (event.x, event.y)
        self.set_crop_area()
        # print("END!")
        self.canvas.delete(self.current_rect)
        self.current_rect = None

    def undo(self):
        if not self.undo_cache:
            print("Nothing to undo!")
            return
        self.edited_img = self.undo_cache.pop()
        self.edited_imgTk = ImageTk.PhotoImage(self.edited_img)
        self.canvas.create_image(
            2*thumboffset + self.img_w, thumboffset, anchor=tk.NW, image=self.edited_imgTk)

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
            master=self.toolButtons, text='BW', command=self.init_bw_frame)
        self.drawButton = tk.Button(
            master=self.toolButtons, text='Draw', command=self.init_draw_frame)

        self.blankFrame = tk.LabelFrame(
            self._frame, text='Mode tools', padx=40)
        self.blankButton = tk.Button(self.blankFrame, padx=20)

        self._frame.grid(pady=frameoffset)
        self.blankFrame.grid(row=0, column=0)
        self.toolButtons.grid(row=0, column=1)

        self.blankButton.grid(row=0, column=0)

        self.drawButton.grid(row=0, column=0)
        self.binarizeButton.grid(row=0, column=1)

    def init_draw_frame(self):
        '''draw stuff'''
        self.first_menu_step()

        self.toolButtons = tk.LabelFrame(self._frame, text='Utilities')
        self.binarizeButton = tk.Button(
            master=self.toolButtons, text='BW', command=self.init_bw_frame)
        self.backButton = tk.Button(
            master=self.toolButtons, text='Back', command=self.init_base_frame)

        self.drawToolsFrame = tk.LabelFrame(
            self._frame, text='Draw tools', padx=0)
        # self.drawPencil =

        self._frame.grid(pady=frameoffset)
        self.toolButtons.grid(row=0, column=0)

        self.backButton.grid(row=0, column=0)
        self.binarizeButton.grid(row=0, column=1)

    def init_bw_frame(self):
        self.first_menu_step()

        self.toolButtons = tk.LabelFrame(self._frame, text='Utilities')
        self.drawButton = tk.Button(
            master=self.toolButtons, text='BW', command=self.init_draw_frame)
        self.backButton = tk.Button(
            master=self.toolButtons, text='Back', command=self.init_base_frame)

        self.bwToolsFrame = tk.LabelFrame(
            self._frame, text='Black/White tools', padx=0)
        self.bwThresholdScale = tk.Scale(
            master=self.bwToolsFrame, from_=0, to=255, orient=tk.HORIZONTAL, label='Threshold', command=self.updateBWT)
        self.bwThresholdScale.set(self.bw_thresh)
        self.bwInc = tk.Button(
            self.bwToolsFrame, text='+1', command=self.incBWT)
        self.bwDec = tk.Button(
            self.bwToolsFrame, text='-1', command=self.decBWT)

        self._frame.grid(pady=frameoffset)
        self.bwToolsFrame.grid(row=0, column=0)
        self.toolButtons.grid(row=0, column=1)

        # add these buttons back in later
        self.bwDec.grid(row=0, column=0)
        self.bwThresholdScale.grid(row=0, column=1)
        self.bwInc.grid(row=0, column=2)

        self.drawButton.grid(row=0, column=0)
        self.backButton.grid(row=0, column=1)

    def incBWT(self):
        self.bw_thresh += 1
        self.bwThresholdScale.set(self.bw_thresh)

    def decBWT(self):
        self.bw_thresh -= 1
        self.bwThresholdScale.set(self.bw_thresh)

    def updateBWT(self, event):
        self.bw_thresh = self.bwThresholdScale.get()

        # please restore this later
        # self.undo_cache.append(np.copy(self.edited_img))

        self.edited_img = Image.fromarray(cv.threshold(
            cv.cvtColor(np.array(self.image), cv.COLOR_RGB2BGR),
            thresh=self.bw_thresh,
            maxval=255,
            type=cv.THRESH_BINARY
        )[1])

        #print(type(self.edited_img))

        self.display_edited()

    def init_basic_menu(self):
        self.basicButtons = tk.LabelFrame(self._frame, text='Basics')

        self.cropsButton = tk.Button(self.basicButtons, text='Crop')
        self.resetButton = tk.Button(self.basicButtons, text='Reset')
        self.undoButton = tk.Button(
            self.basicButtons, text='Undo', command=self.undo)
        self.exitButton = tk.Button(
            self.basicButtons, text='Exit', command=self.quit)

        self.basicButtons.grid(row=0, column=2, padx=0)
        self.cropsButton.grid(row=0, column=0)
        self.resetButton.grid(row=0, column=1)
        self.undoButton.grid(row=0, column=2)
        self.exitButton.grid(row=0, column=4)

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

        self.edited_img = self.image.copy()

        self.displayimage()

    def displayimage(self):
        rr = (self.region_rect.left, self.region_rect.top,
              self.region_rect.right, self.region_rect.bottom)
        self.image_thumb = self.image.crop(rr)
        self.image_thumb.thumbnail(thumbsize, Image.ANTIALIAS)

        self.image_thumb_rect = Rect(self.image_thumb.size)

        self.photoimage = ImageTk.PhotoImage(self.image_thumb)
        self.img_w, self.img_h = self.image_thumb.size
        self.canvas.configure(
            width=(2*self.img_w + 3 * thumboffset),
            height=(self.img_h + 2 * thumboffset))

        self.undo_cache.append(self.edited_img)  # this might duplicate edits

        self.edited_imgTk = self.edited_img.crop(rr)
        self.edited_imgTk.thumbnail(thumbsize, Image.ANTIALIAS)
        self.edited_imgTk = ImageTk.PhotoImage(self.edited_imgTk)

        self.canvas.create_image(
            thumboffset,
            thumboffset,
            anchor=tk.NW,
            image=self.photoimage)

        if self.editedCanvas is None:
            self.editedCanvas = self.canvas.create_image(
                2*thumboffset + self.img_w, thumboffset, anchor=tk.NW, image=self.edited_imgTk)
        else:
            self.canvas.itemconfig(self.editedCanvas, image=self.edited_imgTk)

        x_scale = float(self.region_rect.w) / self.image_thumb_rect.w
        y_scale = float(self.region_rect.h) / self.image_thumb_rect.h
        self.scale = (x_scale, y_scale)
        self.redraw_rect()

    ''' Rect ops '''

    def redraw_rect(self):
        for croparea in self.crop_rects:
            self.drawrect(croparea.rescale_rect(self.scale, self.x0, self.y0))

    def drawrect(self, rect):
        bbox = (rect.left, rect.top, rect.right, rect.bottom)
        cr = self.canvas.create_rectangle(
            bbox, activefill='', fill='red', stipple='gray25')
        self.canvas_rects.append(cr)


def dummy():
    print('dummy')


def main():
    root = Cropper()
    root.mainloop()


if __name__ == '__main__':
    main()
