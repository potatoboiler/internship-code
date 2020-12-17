import os
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

    def __init__(self, master=None, image=None, filename=None, photoimage=None):
        tk.Tk.__init__(self, master)
        self.grid()
        self.initCanvas() 


        # holds separate menu frames
        self._frame = tk.Frame(master=self)
        self._frame.grid(row=1, column=1)

        self.edited_img = None
        self.undo_cache = list()

        '''create menu bar'''
        self.init_menu_bar()
        self.config(menu=self.menubar)

        if __name__ == '__main__' or image is None:
            self.getFile()
        else:
            self.image = image
            self.filename = filename
        self.loadimage()
        
        # to be honest, image and photoimage parameters are kind of redundant and can probably just be refactored to be the same thing. 
        # photoimage basically allows passing of image from previous window. This is not implemented yet, but this should ideally allow for the original, non-binarized image as well as the binarized image to both be passed at the same time.
        self.ext_pi = None
        if photoimage is not None:
            self.ext_pi = photoimage.copy()
        else:
            self.ext_pi = None
        self.displayimage()

        # initializes Save, Reset, Undo, Exit buttons
        self.init_basicbuttons()

        # initializes basic pen properties
        self.color = 'white'
        self.drawsize = 3
        self.thickness_sv = tk.StringVar()  # used for thickness display
        self.thickness_sv.set(self.drawsize)

        # initializes buttons that modify drawing functions
        self.init_drawbuttons()

    '''window initiators'''

    # initializes menu bar at top of GUI
    def init_menu_bar(self):
        ''' Initiates menu bar at top of GUI '''
        self.menubar = tk.Menu(master=self)
        self.create_filemenu(menubar=self.menubar)

    # initializes canvas with basic features and binds the mouse to the drawing feature
    def initCanvas(self):
        ''' Initializes canvas to display loaded image, but doesn't actually display yet. Display is handled in loadimage() and displayimage() '''
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

    def drawingcanvas_m1cb(self, event):
        ''' Once left-click button is held down, copies the image before drawing to the undo cache and calls the draw-function to the location of the mouse. '''
        self.undo_cache.append(self.edited_img.copy())
        self.drawingcanvas_paint(event)

    def drawingcanvas_paint(self, event):
        ''' Draws by updating the underlying edited_img, then pushing to canvas. this is way more expensive than updating canvas by itself.
        This can be improved (made lighter and faster) by separately drawing onto the canvas display and the original image itself, however this may result in mismatch between the displayed image and the image held in memory.
        '''

        # can i perhaps make these instance variables to eliminate allocation call?
        scaledx, scaledy = (event.x*self.scale[0], event.y*self.scale[1])
        temp = self.drawsize/2

        # draws circle on the image held in memory
        self.draw_handle.ellipse([scaledx - temp, scaledy - temp,
                                  scaledx + temp, scaledy + temp], fill=self.color, width=self.drawsize)

        # updates the displayed image on the canvas
        self.update_editedTk()
        self.drawingcanvas.itemconfig(
            self.editedCanvas, image=self.edited_imgTk)
        #print(event.x, event.y)

    def update_editedTk(self):
        ''' Updates the canvas to display the current version of edited_img. '''
        self.edited_imgTk = self.edited_img.crop(self.rr)
        self.edited_imgTk.thumbnail(thumbsize, Image.ANTIALIAS)
        self.edited_imgTk = ImageTk.PhotoImage(self.edited_imgTk, master=self)

        # ensures that drawing functionality is not lost by reattaching the ImageDraw module to the edited image
        self.draw_handle = ImageDraw.Draw(self.edited_img)

    def reset(self):
        ''' Resets the edited image to whatever the original image was. '''
        self.undo_cache.append(self.edited_img.copy())
        self.edited_img = self.image.copy().convert('RGB')
        self.display_edited()

    def undo(self):
        ''' Undo '''
        if not self.undo_cache:
            print("Nothing to undo!")
            return
        self.edited_img = self.undo_cache.pop()
        self.update_editedTk()
        self.drawingcanvas.itemconfig(
            self.editedCanvas, image=self.edited_imgTk)

    def passNext(self):
        ''' Passes the current version of the edited image to the next window (i.e. from the binarization window to the drawing window) '''
        self.edited_img.save('temp' + self.extension())
        self.quit()

    '''Menu stuff'''

    def create_filemenu(self, menubar):
        ''' creates File menu in toolbar at top of GUI '''
        filemenu = tk.Menu(master=menubar, tearoff=0)
        filemenu.add_command(label="Open", command=self.getFile)
        filemenu.add_command(label="Save edited image", command=self.saveED)
        filemenu.add_separator()
        filemenu.add_command(label="Exit", command=self.quit)
        menubar.add_cascade(label="File", menu=filemenu)

    def init_basicbuttons(self):
        ''' initiates buttons and menu for saving, exiting, and moving to next window '''
        self.basicButtons = tk.LabelFrame(self._frame, text='Basics')

        self.resetButton = tk.Button(
            self.basicButtons, text='Reset', command=self.reset)
        self.undoButton = tk.Button(
            self.basicButtons, text='Undo', command=self.undo)
        self.exitButton = tk.Button(
            self.basicButtons, text='Exit', command=self.quit)
        self.saveButton = tk.Button(
            self.basicButtons, text='Save edited', command=self.saveED)

        if __name__ != '__main__':
            self.exitButton.config(text='Next', command=self.passNext)

        self.basicButtons.grid(row=1, column=1)

        self.saveButton.grid(row=0, column=0)
#        self.resetButton.grid(row=0, column=1)
        self.undoButton.grid(row=0, column=2)
        self.exitButton.grid(row=0, column=4)

    def init_drawbuttons(self):
        ''' initiates menu and buttons for drawing functionality, created upon startup '''
        self.drawButtons = tk.LabelFrame(self._frame, text='Drawing tools')

        self.thickChange = tk.LabelFrame(
            self.drawButtons, text='Thickness settings')
        self.thicknessScale = tk.Scale(
            master=self.thickChange,
            from_=0, to=20,
            orient=tk.HORIZONTAL,
            label='Thickness',
            command=self.updateThickness)
        self.thicknessScale.set(self.drawsize)

        self.colorButtons = tk.LabelFrame(self.drawButtons, text='Colors')
        self.blackButton = tk.Button(
            self.colorButtons, text='Black', command=self.makeBlack)
        self.whiteButton = tk.Button(
            self.colorButtons, text='White', command=self.makeWhite, relief=tk.SUNKEN, state='disabled')

        self.drawButtons.grid(row=1, column=0)
        self.thickChange.grid(row=1, column=0)
        self.colorButtons.grid(row=1, column=1)

        self.thicknessScale.grid()

        self.blackButton.grid(row=0, column=0)
        self.whiteButton.grid(row=0, column=1)

    def makeBlack(self):
        ''' makes the pen color black '''
        self.color = 'black'
        self.whiteButton.config(state='normal', relief=tk.FLAT)
        self.blackButton.config(state='disabled', relief=tk.SUNKEN)

    def makeWhite(self):
        ''' makes the pen color white '''
        self.color = 'white'
        self.whiteButton.config(state='disabled', relief=tk.SUNKEN)
        self.blackButton.config(state='normal', relief=tk.FLAT)

    def updateThickness(self, event):
        ''' changes thickness of the pen '''
        self.drawsize = self.thicknessScale.get()
        self.thickness_sv.set(self.drawsize)

    ''' file ops '''

    def getFile(self):  # should return image
        ''' gets file from file dialog '''
        self.file = tkfd.askopenfile(mode='rb', filetypes=[
            ('Image Files', '.jpg .JPG .jpeg .JPEG .png .PNG .tif .TIF .tiff .TIFF'),
            ('TIFF Image Files', '.tif .TIF .tiff .TIFF')
        ])
        self.image = Image.open(self.file)
        self.filename = self.file.name

        # need to redraw canvas and wipe stored crop metadata

    def loadimage(self):
        ''' loads the image file from getFile() into the GUI, placing the original image on the left half and editable version on the right '''
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
        ''' Creates a copy of the loaded image, and crops the copy, to display onto the canvas. The original image is preserved. The size parameters thumbsize may be changed through the thumbsize tuple at the top of the file. '''
        # size of original image
        self.rr = (self.region_rect.left, self.region_rect.top,
                   self.region_rect.right, self.region_rect.bottom)       
        if self.ext_pi is not None:
            self.image_thumb = self.ext_pi.crop(self.rr)
        else:
            self.image_thumb = self.image.crop(self.rr)
        self.image_thumb.thumbnail(thumbsize, Image.ANTIALIAS)

        # size of this is size of downscaled image
        self.image_thumb_rect = Rect(self.image_thumb.size)

        self.photoimage = ImageTk.PhotoImage(self.image_thumb, master=self)
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
        ''' Displays edited image. If it doesn't already exist, then places it onto canvas the same way displayimage() does. If it does, then simply updates canvas with new image. '''
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
