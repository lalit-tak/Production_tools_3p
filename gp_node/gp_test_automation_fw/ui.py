import Tkinter
import sys
root=Tk()
root.filename

class CoreGUI(object):
    def __init__(self, parent):
        text_box = Tkinter.Text(parent, state=Tkinter.DISABLED)
        text_box.pack()

        output_button = Tkinter.Button(parent, text="Output", command=self.main)
        output_button.pack()

    def main(self):
        print "Std Output"
        raise ValueError("Std Error")

root = Tkinter.Tk()
CoreGUI(root)
root.mainloop()

# from tkinter import * 
# a= Tk() 
# def mfileopen():
# 	file1=askopenfilename()
# 	label=Label(text=file1).pack()
# # root.fileName = filedialog.askopenfilename (filetypes=(("Python Stuff", ".PY"), ("All files","*.*"))) 
# # print(root.procedure) # prints filename 
# # # onto terminal 
# # root.title(root.procedure) 
# # # put filename into # title bar 
# # #read the contents of the file 
# # # into the variable: text # print it onto the screen for shits and giggles 
# # text1 = open(root.python).read() 
# # print(text1) # zee buffer: 'text1' 
# # T = Text(root, height=15, width=60) 
# # T.pack() # pack that textbox into # the root window 
# # T.insert(END,text1) #insert all the text up to # just after the last char # in: text1 
# # ### 
# a.mainloop()﻿


