import sys
from Tkinter import *
from ScrolledText import *
from turtle import *
import tkFileDialog
import tkMessageBox


#adjust these as you see fit
render_width = 600
render_border = 20

#the height of the rendered mat is based on the width set above
render_height = render_width/2

pen_down = 0

def draw_mat():
    render_window.create_rectangle(2, 2, render_width+2*render_border,\
                                   render_height+2*render_border,\
                                   fill="red")
    for i in range(13):
        render_window.create_line(i*((render_width)/12.0)+render_border, render_border/2,\
                                  i*((render_width)/12.0)+render_border, render_border)
        render_window.create_line(i*(render_width/12.0)+render_border, render_height+render_border,\
                                  i*(render_width/12.0)+render_border, render_height+render_border*1.5)
    for i in range(7):
        render_window.create_line(render_border/2, i*(render_height/6.0)+render_border,\
                                   render_border, i*(render_height/6.0)+render_border)
        render_window.create_line(render_width+render_border, i*(render_height/6.0)+render_border,\
                                   render_width+render_border*1.5, i*(render_height/6.0)+render_border)

def save_file():
    pass

def load_file():
    pass

def simulate_cut():
    pass

def cut_on_cutter():
    pass
    
def exit_this():
    exit()
    
# main window
root = Tk()
root.title("Python implementation of Risk")

#buttons
f = Frame(root, pady=5)
f.pack(side=TOP)

load_button = Button(f, text="Load", command=load_file, width=20)
load_button.pack(side=LEFT, expand=1, padx=5)

save_button = Button(f, text="Save", command=save_file, width=20)
save_button.pack(side=LEFT, expand=1, padx=5)

simulate_button = Button(f, text="Simulate", command=simulate_cut, width=20)
simulate_button.pack(side=LEFT, expand=1, padx=5)

exit_button = Button(f, text="Exit", command=exit_this, width=20)
exit_button.pack(side=LEFT, expand=1, padx=5)

#label above board
w = Label(root, text="Python Risk")
w.pack(side=TOP)

#canvas that shows mat
render_window = Canvas(root, width=(render_width+2*render_border), height=(render_height+2*render_border))
render_window.pack()
#draw_mat()

#canvas for rendering turtle - placed inside mat canvas
turtle_canvas = Canvas(render_window, width=render_width, height=render_height, bd=0, highlightthickness=0)
turtle_canvas.place(x=render_border, y=render_border)
my_turtle = RawTurtle(turtle_canvas)

#label above code
w = Label(root, text="Logo Code")
w.pack(side=TOP)

#code entry field
code = ScrolledText(root, width=80, height=5)
code.pack(fill=BOTH, expand=1)

root.mainloop()

