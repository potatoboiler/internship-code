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


class Cropper(tk.Tk, CropperMenuBar):

    def __init__(self, master=None):
        tk.Tk.__init__(self, master)
        pass

    '''window initiators'''

    def init_file_menu(self):
        menubar = tk.Menu(self)

    def init_canvas(self, image):
        pass

    def call_frame(self, frameobj):
        pass

    '''Menu stuff'''

    def create_filemenu(self, menubar):
        filemenu = tk.Menu(master=menubar, tearoff=0)
        filemenu.add_command(label="Open", command=self.getFile())
        filemenu.add_separator()
        filemenu.add_command(label="Exit", command=self.quit)
        menubar.add_cascade(label="File", menu=filemenu)


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


class init_frame(tk.Frame):
    pass


class edit_frame(tk.Frame):
    pass


class bw_frame(tk.Frame):
    pass


class crop_edit_frame(tk.Frame):
    pass


def main():
    root = Cropper()
    root.mainloop()


if __name__ == '__main__':
    main()
