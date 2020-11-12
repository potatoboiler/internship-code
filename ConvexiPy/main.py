import os
from tkinter import filedialog as tkfd

from PIL import Image

from bw import BW
from crop import ConvexCropper
from retouch import Retouch

file = tkfd.askopenfile(mode='rb', filetypes=[
    ('Image Files', '.jpg .JPG .jpeg .JPEG .png .PNG .tif .TIF .tiff .TIFF'),
    ('TIFF Image Files', '.tif .TIF .tiff .TIFF')
])
image = Image.open(file)
photoimage = image.copy()
filename = file.name
extension = os.path.splitext(filename)[1]
print(extension)

root = BW(image=image, filename=filename)
root.mainloop()

image = Image.open('temp' + extension)
root = Retouch(image=image, filename=filename)
root.mainloop()

image = Image.open('temp' + extension)
root = ConvexCropper(image=image, filename=filename, photoimage=photoimage)
root.mainloop()
