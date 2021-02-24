# This file will later be used to collect some of the basic methods that don't change between the different tools and make the code more compact
import tkinter as tk
from tkinter import filedialog as tkfd


class GUItool(tk.Tk):

    def __init__(self, master=None):
        tk.Tk.__init__(self, master)

        self._frame = tk.Frame(master=self)
        self._frame.grid(row=1, column=1)

        self.initCanvas()
        self.init_basicbuttons()

    def initCanvas(self):
        ''' May be extended '''
        self.canvas = tk.Canvas(
            self, height=500, width=500, relief=tk.SUNKEN)
        self.canvas.grid()

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
        self.resetButton.grid(row=0, column=1)
        self.undoButton.grid(row=0, column=2)
        self.saveButton.grid(row=0, column=3)
        self.exitButton.grid(row=0, column=4)

    def reset(self):
        ''' Reset processed file/image to original state '''
        raise NotImplementedError

    def undo(self):
        ''' Undo last change '''
        raise NotImplementedError

    def saveED(self):
        ''' Save edited file/image '''
        raise NotImplementedError

    def passNext(self):
        ''' Perform operations to pass to another window '''
        raise NotImplementedError


if __name__ == '__main__':
    x = GUItool()
    x.mainloop()
