from Tkinter import *

class PyDrillNoteBook:
    def __init__(self,master,sticky=None):
        self.master = master
        self.pages = {}
        
        #if sticky:
        self.sticky=sticky
        #else:
        #    self.sticky=W
        self.mainFrame = Frame(self.master)
        self.buttonFrame = Frame(self.mainFrame)
        self.displayFrame = Frame(self.mainFrame)
        
        self.gridCount = 0
        self.currentPage = None

    def addPage(self,title,frame):
        
        self.pages[title] = frame
        
        self.gridCount += 1
        if not(self.currentPage):
            self.currentPage = frame
            self.currentPage.grid(sticky=self.sticky)

        newButton = Button(self.buttonFrame,text=str(title),command=lambda: self.switchPage(title))
        newButton.grid(row=0,column=self.gridCount)

    def switchPage(self,page):
        self.currentPage.grid_remove()
        self.pages[page].grid(sticky=self.sticky)
        self.currentPage = self.pages[page]


    def __call__(self):
        return self.displayFrame

    def grid(self,row=0,column=0,**kw):
        self.mainFrame.grid(row=row,column=column,**kw)
        self.buttonFrame.grid(row=0,column=0,sticky=N+W)
        self.displayFrame.grid(row=1,column=0)

class PyDrillWindow:
    def __init__(self,master,height=0,width=0):
        self.top = Frame(master)
        self.width = Frame(self.top,width=width)
        self.height = Frame(self.top,height=height)
        self.body = Frame(self.top)

    def __call__(self):
        return self.body

    def grid(self,row=0,column=0,**kw):
        self.top.grid(row=row,column=column,**kw)
        self.width.grid(row=0,column=1)
        self.height.grid(row=1,column=0)
        self.body.grid(row=1,column=1,sticky=N+W)

class PyDrillLabel:
    def __init__(self,master,label):
        self.container = Frame(master)
        self.label = Label(self.container,text=str(label))
        self.display = Label(self.container,text='')
        
    def grid(self,row=0,column=0,**kargs):
        self.label.grid(row=0,column=0)
        self.display.grid(row=1,column=0)
        
        self.container.grid(row=row,column=column,**kargs)
    
        
    
class PyDrillToolDataLabel(PyDrillLabel):
    def __init__(self,master,label):
        PyDrillLabel.__init__(self,master,label)
    
    def newData(self,toolData):
        self.data = toolData
        myStr = str(int(self.data.value,16)) + "  @  " + str(self.data.timeStamp)
        self.display.configure(text=myStr)
