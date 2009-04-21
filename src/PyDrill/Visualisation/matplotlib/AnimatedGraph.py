# For detailed comments on animation and the techniqes used here, see
# the wiki entry http://www.scipy.org/Cookbook/Matplotlib/Animations

import matplotlib
matplotlib.use('TkAgg')

import sys
import pylab as p
import numpy as npy
import time
import Tkinter as Tk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg
import threading

root = Tk.Tk()
root.wm_title("Embedding")


class AnimatedGraph:
    def __init__(self,x,y):
        f = matplotlib.figure.Figure(figsize=(5,4),dpi=100)
        #f = matplotlib.figure.Figure(dpi=100)
        ax = f.add_subplot(111)
        canvas = ax.figure.canvas
        
        line, = p.plot(x,y, animated=True, lw=2)

        canvas = FigureCanvasTkAgg(f, master=root)
        canvas.show()

        canvas.get_tk_widget().grid()
        
        toolbar = NavigationToolbar2TkAgg( canvas, root )
        toolbar.update()
        
        canvas._tkcanvas.pack(side=Tk.TOP, fill=Tk.BOTH, expand=1)

        p.subplots_adjust(left=-0.1,bottom=0.0)
        manager = p.get_current_fig_manager()
        manager.window.after(100, self.run)

        self.canvas = canvas
        self.ax = ax
        self.line = line
        self.x = x
        self.y = y
    def run(self,*args):

    
        class MyThread(threading.Thread):
            def __init__(self,g):
                self.g = g
                threading.Thread.__init__(self)

            def run(self):
                background = self.g.canvas.copy_from_bbox(self.g.ax.bbox)
                # for profiling
                tstart = time.time()
                self.cnt = 0
                while 1:
                    # restore the clean slate background
                    self.g.canvas.restore_region(background)
                    # update the data
                    print self.g.y[0]
                    self.g.line.set_ydata(self.g.y)
                    # just draw the animated artist
                    self.g.ax.draw_artist(self.g.line)
                    # just redraw the axes rectangle
                    self.g.canvas.blit(self.g.ax.bbox)

                    time.sleep(.01)

        mt = MyThread(self)
        mt.start()

                    
# create the initial line
x = npy.arange(0,2*npy.pi,0.01)
y = npy.sin(x)

g = AnimatedGraph(x,y)

class MyThread2(threading.Thread):
    def run(self):
        self.cnt = 0
        while(1):
            print g.y[0]
            g.y = npy.sin(x+self.cnt/10.0)
            self.cnt += 1
            time.sleep(0.01)
            
t2 = MyThread2()
t2.start()
#p.show()
Tk.mainloop()



