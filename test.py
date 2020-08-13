from tkinter import *
import tkinter

top = Tk()
left = Frame(top)
right= Frame(top)
C1 = Checkbutton(left, text="RUNOOB",
                 onvalue=1, offvalue=0, height=5,
                 width=20)
C2 = Checkbutton(right, text="RUNOOB",
                 onvalue=1, offvalue=0, height=5,
                 width=20)
C1.pack()
C2.pack()
left.pack(side=LEFT)
right.pack(side=RIGHT)
top.mainloop()