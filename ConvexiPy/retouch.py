import tkinter as tk
from tkinter import filedialog as tkfd

import cv2 as cv
import numpy as np
from PIL import Image, ImageDraw, ImageTk

from rect import Rect

thumbsize = 896, 608
thumboffset = 16
frameoffset = 10

# edited_img --> ImageDraw (then I also need to change how the undo feature works)


class Retouch(tk.Tk):

    def __init__(self, master=None, image=None):
        tk.Tk.__init__(self, master)
        self.grid()
        self.initCanvas()

        # holds separate menu frames
        self._frame = None

        self.edited_img = None
        self.undo_cache = list()

        '''create menu bar'''
        self.init_menu_bar()
        self.config(menu=self.menubar)

        if __name__ == '__main__' or image is None:
            self.getFile()
            self.loadimage()
        else:
            self.image = image
            self.loadimage()
        self.init_basicbuttons()

        self.color = 'white'
        self.drawsize = 1

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
        # display reference canvas
        self.canvas = tk.Canvas(self, height=1, width=1)
        self.drawingcanvas = tk.Canvas(
            self, height=1, width=1)  # canvas drawn to
        self.canvas.grid(row=0, column=0)
        self.drawingcanvas.grid(row=0, column=1)

        self.drawingcanvas.bind('<Button-1>', self.drawingcanvas_m1cb)
        self.drawingcanvas.bind('<B1-Motion>', self.drawingcanvas_paint)

        # contains canvas image object for edited img
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

    def saveED(self):
        self.saveImage(self.edited_img)

    def drawingcanvas_m1cb(self, event):
        self.undo_cache.append(self.edited_img.copy())
        self.drawingcanvas_paint(event)

    def drawingcanvas_paint(self, event):
        '''draws by updating the underlying edited_img, then pushing to canvas. this is way more expensive than updating canvas and '''

        # can i perhaps make these class members to eliminate allocation call?
        scaledx, scaledy = (event.x*self.scale[0], event.y*self.scale[1])
        temp = self.drawsize/2

        self.draw_handle.line([scaledx - temp, scaledy - temp,
                               scaledx + temp, scaledy + temp], fill=self.color, width=self.drawsize)

        self.update_editedTk()
        self.drawingcanvas.itemconfig(
            self.editedCanvas, image=self.edited_imgTk)
        #print(event.x, event.y)

    def update_editedTk(self):
        self.edited_imgTk = self.edited_img.crop(self.rr)
        self.edited_imgTk.thumbnail(thumbsize, Image.ANTIALIAS)
        self.edited_imgTk = ImageTk.PhotoImage(self.edited_imgTk)

        # ensure that drawing functionality is not lost
        self.draw_handle = ImageDraw.Draw(self.edited_img)

    def undo(self):
        if not self.undo_cache:
            print("Nothing to undo!")
            return
        self.edited_img = self.undo_cache.pop()
        self.update_editedTk()
        self.drawingcanvas.itemconfig(
            self.editedCanvas, image=self.edited_imgTk)

    '''Menu stuff'''

    def create_filemenu(self, menubar):
        filemenu = tk.Menu(master=menubar, tearoff=0)
        filemenu.add_command(label="Open", command=self.getFile)
        filemenu.add_command(label="Save edited image", command=self.saveED)
        filemenu.add_separator()
        filemenu.add_command(label="Exit", command=self.quit)
        menubar.add_cascade(label="File", menu=filemenu)

    def init_basicbuttons(self):
        self.basicButtons = tk.LabelFrame(self._frame, text='Basics')

        self.resetButton = tk.Button(self.basicButtons, text='Reset')
        self.undoButton = tk.Button(
            self.basicButtons, text='Undo', command=self.undo)
        self.exitButton = tk.Button(
            self.basicButtons, text='Exit', command=self.quit)

        self.basicButtons.grid(row=1)
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

        self.edited_img = self.image.copy().convert('RGB')
        self.draw_handle = ImageDraw.Draw(self.edited_img)
        # print(type(self.edited_img))

        self.displayimage()
        self.display_edited()

    def displayimage(self):  # to do: substitute all edited image operations
        # size of original image
        self.rr = (self.region_rect.left, self.region_rect.top,
                   self.region_rect.right, self.region_rect.bottom)
        self.image_thumb = self.image.crop(self.rr)
        self.image_thumb.thumbnail(thumbsize, Image.ANTIALIAS)

        # size of this is size of downscaled image
        self.image_thumb_rect = Rect(self.image_thumb.size)

        self.photoimage = ImageTk.PhotoImage(self.image_thumb)
        self.img_w, self.img_h = self.image_thumb.size

        self.canvas.configure(
            width=(self.img_w + thumboffset),
            height=(self.img_h + 2 * thumboffset))

        self.canvas.create_image(
            thumboffset,
            0,
            anchor=tk.NW,
            image=self.photoimage)

        # ratio of original width to downscaled width
        x_scale = float(self.region_rect.w) / self.image_thumb_rect.w
        y_scale = float(self.region_rect.h) / self.image_thumb_rect.h
        self.scale = (x_scale, y_scale)

    def display_edited(self):
        self.update_editedTk()

        self.drawingcanvas.configure(
            width=(self.img_w + thumboffset),
            height=(self.img_h + 2 * thumboffset))

        if self.editedCanvas is None:
            self.editedCanvas = self.drawingcanvas.create_image(
                0, 0, anchor=tk.NW, image=self.edited_imgTk)
        else:
            self.canvas.itemconfig(self.editedCanvas, image=self.edited_imgTk)


def main():
    root = Retouch()
    root.mainloop()


if __name__ == '__main__':
    main()
