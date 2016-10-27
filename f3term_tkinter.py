
# -*- coding: UTF-8 -*-

import pygame, sys, time, random, string
from Tkinter import *
import Tkinter
from PIL import Image, ImageTk
from pygame.locals import * 

pygame.init() 

class Example(Frame):

    def __init__(self, parent):
        Frame.__init__(self, parent)            
        self.parent = parent        
        self.initUI()

    def initUI(self):
        self.parent.title("PISE")
        self.pack(fill=BOTH, expand=1)

root = Tk()
root.geometry("800x600")
app = Example(root)

im = Image.open('f3term.png')
tkimage = ImageTk.PhotoImage(im)
myvar=Tkinter.Label(root,image = tkimage)
myvar.place(x=0, y=0, relwidth=1, relheight=1)

t = Text(root)
t.pack()
root.after(1000,t.insert,'end',"111111111\n")
root.after(2000,t.insert,'end',"222222222\n")

def beenClicked1():
    pass

def beenClicked5():
    pass



root.mainloop()

