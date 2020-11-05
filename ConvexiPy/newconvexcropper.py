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


class Cropper(tk.Tk):
    pass


class init_frame(tk.Frame):
    pass


class alt_frame(tk.Frame):
    pass


def main():
    root = Cropper()
    root.mainloop()


if __name__ == '__main__':
    main()
