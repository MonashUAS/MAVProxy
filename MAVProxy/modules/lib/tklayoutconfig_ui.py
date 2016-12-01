from MAVProxy.modules.lib import mp_util
import tkinter as tk
import tkFont
import subprocess as sp

from math import ceil

class LayoutConfigFrame(tk.Frame):
    """ The main frame of the layout configurator."""

    def __init__(self, state, mainwindow):
        self.state = state
        self.mainwindow = mainwindow
        self.winList  = []
        self.maxCharLen  = 0

        # Create Frame
        tk.Frame.__init__(self, master=self.mainwindow)
        self.rows = 1
        self.grid(row=100,column=8)
        self.grid_rowconfigure(0,weight=1)
        
        # Add Listboxes
        # List Windows List
        self.getWindowList()
        self.rows = int(ceil(len(self.winList)/2.0)*2) # Round up to the nearest even number
        self.lbFont = tkFont.Font(size=11)
        self.lb1 = tk.Listbox(self,selectmode=tk.EXTENDED,height=self.rows,width=self.maxCharLen,font=self.lbFont)
        self.lb2 = tk.Listbox(self,selectmode=tk.EXTENDED,height=self.rows,width=self.maxCharLen,font=self.lbFont)
        for i in range(0,len(self.winList)):
            self.lb1.insert(i,self.winList[i])
            self.lb2.insert(i,self.winList[i])
        self.grid(row=self.rows,column=8)
        self.lb1.grid(row=1,rowspan=self.rows,column=0)
        # Save Windows List

        self.lb2.grid(row=1,rowspan=self.rows,column=3)
        
        # Add Buttons
        # Get/Save Data Buttons
        self.but1 = tk.Button(self,text="Update Window List",command=self.getWindowList)
        self.but1.grid(row=0,column=0)
        self.but2 = tk.Button(self,text="Load Config File",command=self.loadConfigFile)
        self.but2.grid(row=0,column=1,columnspan=2)
        self.but3 = tk.Button(self,text="Save Config File",command=self.saveConfigFile)
        self.but3.grid(row=0,column=3)
        # Alter List Buttons
        self.but3 = tk.Button(self,text="<<",command=self.moveLeft)
        self.but3.grid(row=self.rows/2,column=1,rowspan=2)
        self.but4 = tk.Button(self,text=">>",command=self.moveRight)
        self.but4.grid(row=self.rows/2,column=2,rowspan=2)
        
        # Add Labels
        self.cmdLabel = tk.Label(self,text='module load <cmd>')
        self.cmdLabel.grid(row=0,column=4)
        self.xlb = tk.Label(self,text='x')
        self.xlb.grid(row=0,column=5)
        self.ylb = tk.Label(self,text='y')
        self.ylb.grid(row=0,column=6)
        self.widthlb = tk.Label(self,text='width')
        self.widthlb.grid(row=0,column=7)
        self.heightlb = tk.Label(self,text='height')
        self.heightlb.grid(row=0,column=8)
        
        ''# Add Entry Boxes - turn this into a function
        self.cmdBoxes = []
        self.xBoxes = []
        self.yBoxes = []
        self.widthBoxes = []
        self.heightBoxes = []
        self.entryFont = tkFont.Font(size=8)
        for i in range(0,self.rows-1):
            self.cmdBoxes.append(tk.Entry(self,bd=1,font=self.entryFont))
            self.cmdBoxes[i].grid(row=i+1,column=4)
            self.xBoxes.append(tk.Entry(self,bd=1,width=5,font=self.entryFont))
            self.xBoxes[i].grid(row=i+1,column=5)
            self.yBoxes.append(tk.Entry(self,bd=1,width=5,font=self.entryFont))
            self.yBoxes[i].grid(row=i+1,column=6)
            self.widthBoxes.append(tk.Entry(self,bd=1,width=5,font=self.entryFont))
            self.widthBoxes[i].grid(row=i+1,column=7)
            self.heightBoxes.append(tk.Entry(self,bd=1,width=5,font=self.entryFont))
            self.heightBoxes[i].grid(row=i+1,column=8)       
        
        self.on_timer() # start timer

    def getWindowList(self,show=False):
        '''Gets the window list for the long names of windows.'''
        p = sp.Popen(["wmctrl","-l"],stdout=sp.PIPE)
        out, err = p.communicate()
        mylist = out.split('\n')
        winNames = []
        charLen = []
        for line in mylist:
            if len(line)>0:
                line = line.split(' ')
                thisLine = " ".join(line[4:])
                winNames.append(thisLine)
                charLen.append(len(thisLine))
                if show:
                    print thisLine
                    
        self.winList = winNames
        self.maxCharLen = int(max(charLen)*0.80)
        if self.maxCharLen > 50:
            self.maxCharLen = 50
        print 'Updated Window List.'


    def loadConfigFile(self):
        '''Loads the configuration file.'''
        pass

    def saveConfigFile(self):
        '''Saves the configuration to file.'''
        pass

    def moveLeft(self):
        '''Moves the selected windows to the left listbox.'''
        pass
    
    def moveRight(self):
        '''Moves the selected windows to the right listbox, to be
        saved in the configuration.'''
        pass

    def on_timer(self):
        '''Main Loop.'''
        state = self.state
        if state.close_event.wait(0.001):
            self.mainwindow.destroy()
            return
        # Get messages
        '''while state.child_pipe_recv.poll():
            obj = state.child_pipe_recv.recv()
            if isinstance(obj, ParamUpdateList):
                print "list"
                for param in obj.params:
                    self.__parse_param(param)
            elif isinstance(obj, ParamUpdate):
                print "single"
                self.__parse_param(obj)'''
        self.mainwindow.after(100, self.on_timer)
