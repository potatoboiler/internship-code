"""
A few notes:
Most of the ideas for the crop.py tool were taken from the cropper-tk library, found here:
https://github.com/ImageProcessing-ElectronicPublications/python-cropper-tk

The code can definitely be cleaned up, and some common functions between the three sub-tools can be implemented in a parent GUI class. 
When I was developing this, I focused on making each tool independently functional, so I just copy-pasted code. Might be a good project to also boost the tool's efficiency.

Functions common to all sub-tools will be documented a bit more thoroughly in bw.py

It may be possible to convert directly to a single-channel, truly binary image using color-space conversion, but I have to investigate how this might change other parts of the code.
https://docs.opencv.org/master/db/d64/tutorial_js_colorspaces.html 


"""
import os
from tkinter import filedialog as tkfd

from PIL import Image, ImageOps

from bw import BW
from crop import ConvexCropper
from retouch import Retouch

file = tkfd.askopenfile(mode='rb', filetypes=[
    ('Image Files', '.jpg .JPG .jpeg .JPEG .png .PNG .tif .TIF .tiff .TIFF'),
    ('TIFF Image Files', '.tif .TIF .tiff .TIFF')
])
image = ImageOps.grayscale(Image.open(file))
photoimage = image.copy()
filename = file.name
extension = os.path.splitext(filename)[1]
# print(extension)

root = BW(image=image, filename=filename)
root.mainloop()
root.destroy()

image = Image.open('temp' + extension)
root = Retouch(image=image, filename=filename)
root.mainloop()
root.destroy()

image = Image.open('temp' + extension)
root = ConvexCropper(image=image, filename=filename)
root.mainloop()