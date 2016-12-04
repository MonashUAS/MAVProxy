from MAVProxy.modules.lib import mp_util
import tkinter as tk
import tkFont
import subprocess as sp

from math import ceil
import tkFileDialog

class LayoutConfigFrame(tk.Frame):
    """ The main frame of the layout configurator."""

    def __init__(self, state, mainwindow):
        self.state = state
        self.mainwindow = mainwindow
        self.winList  = []
        self.maxCharLen  = 0
        self.rows = 15

        # Create Frame
        tk.Frame.__init__(self, master=self.mainwindow)
        self.grid(row=self.rows+1,column=8)
        for i in range(0,self.rows):
            self.grid_rowconfigure(i,weight=0)
        
        # Add Listboxes
        # List Windows List
        self.getWindowList()
        self.lbFont = tkFont.Font(size=11)
        self.lb1 = tk.Listbox(self,selectmode=tk.EXTENDED,height=self.rows,width=self.maxCharLen,font=self.lbFont)
        self.lb2 = tk.Listbox(self,selectmode=tk.EXTENDED,height=self.rows,width=self.maxCharLen,font=self.lbFont)
        # Save Windows List
        for i in range(0,len(self.winList)):
            self.lb1.insert(i,self.winList[i])
        if len(self.winList) < self.rows:
            for i in range(len(self.winList)+1,self.rows+1):
                self.lb1.insert(i,"")
        self.lb1.grid(row=1,rowspan=self.rows,column=0)
        self.lb2.grid(row=1,rowspan=self.rows,column=3)
        if len(self.winList) < self.rows:
            for i in reversed(range(len(self.winList),self.rows+1)):
                self.lb1.delete(i)
        
        # Add Buttons
        # Get/Save Data Buttons
        self.but1 = tk.Button(self,text="Update Window List",command=self.updateWindowList)
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
        # Add set Windows Button
        self.but5 = tk.Button(self,text="Set Windows",command=self.setWindows)
        self.but5.grid(row=2,column=1,columnspan=2,rowspan=2)
        
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
        self.entryFont = tkFont.Font(size=8)
        self.fileEntryBox = tk.Entry(self,bd=1,font=self.entryFont)
        self.fileEntryBox.insert(0,'~/file.cfg')
        self.fileEntryBox.grid(row=1,column=1,columnspan=2)
        self.cmdBoxes = []
        self.xBoxes = []
        self.yBoxes = []
        self.widthBoxes = []
        self.heightBoxes = []
        for i in range(0,self.rows):
            self.cmdBoxes.append(tk.Entry(self,bd=1,font=self.entryFont))
            self.cmdBoxes[i].grid(row=i+1,column=4,sticky='N')
            self.xBoxes.append(tk.Entry(self,bd=1,width=5,font=self.entryFont))
            self.xBoxes[i].grid(row=i+1,column=5,sticky='N')
            self.yBoxes.append(tk.Entry(self,bd=1,width=5,font=self.entryFont))
            self.yBoxes[i].grid(row=i+1,column=6,sticky='N')
            self.widthBoxes.append(tk.Entry(self,bd=1,width=5,font=self.entryFont))
            self.widthBoxes[i].grid(row=i+1,column=7,sticky='N')
            self.heightBoxes.append(tk.Entry(self,bd=1,width=5,font=self.entryFont))
            self.heightBoxes[i].grid(row=i+1,column=8,sticky='N')
           
        
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
                if thisLine not in ['XdndCollectionWindowImp','unity-launcher','unity-panel','unity-dash','Hud','Desktop']:
                    winNames.append(thisLine)
                    charLen.append(len(thisLine))
                    if show:
                        print thisLine
                    
        self.winList = winNames
        self.maxCharLen = int(max(charLen)*0.80)
        if self.maxCharLen > 40:
            self.maxCharLen = 40
        print 'Updated Window List.'

    def updateWindowList(self):
        '''Updates the displayed window list.'''
        # Get New Window List
        self.getWindowList()
        # Reset the listboxes
        self.lb1.delete(0,tk.END)
        for i in range(0,len(self.winList)):
            self.lb1.insert(i,self.winList[i])
        self.lb2.delete(0,tk.END)
        # Clear Entry Boxes
        self.updateEntryBoxes()

    def loadConfigFile(self):
        '''Loads the configuration file.'''
        # Update Window List
        self.updateWindowList()
        # Open File
        oldFile = self.fileEntryBox.get().split('/')
        mydir = '/'.join(oldFile[:-1])
        myfile = oldFile[-1]
        f = tkFileDialog.askopenfile(title='Save Configuration File',defaultextension='.cfg',initialdir=mydir,initialfile=myfile,filetypes=[('Config files','.cfg'),('Text files','.txt')])
        # Read in data
        line = f.readline()
        i = -1
        while line != '':
            i = i + 1
            lineData = line.split(':,:')
            self.lb2.insert(tk.END,lineData[0])
            self.cmdBoxes[i].insert(0,lineData[1])
            self.xBoxes[i].insert(0,lineData[2])
            self.yBoxes[i].insert(0,lineData[3])
            self.widthBoxes[i].insert(0,lineData[4])
            self.heightBoxes[i].insert(0,lineData[5][:-2])
            # Get next line
            line = f.readline()
        # Close file
        f.close()

    def saveConfigFile(self):
        '''Saves the configuration to file.'''
        # Create file to save
        oldFile = self.fileEntryBox.get().split('/')
        mydir = '/'.join(oldFile[:-1])
        myfile = oldFile[-1]
        f = tkFileDialog.asksaveasfile(mode='w',title='Save Configuration File',defaultextension='.cfg',initialdir=mydir,initialfile=myfile,filetypes=[('Config files','.cfg'),('Text files','.txt')])
        if f is None:
            print 'Invalid file.'
            return
        self.fileEntryBox.delete(0,tk.END)
        self.fileEntryBox.insert(0,f.name)
        # Write data to file
        for i in range(0,self.lb2.size()):
            winName = self.lb2.get(i)
            winCmd = self.cmdBoxes[i].get()
            x = self.xBoxes[i].get()
            y = self.yBoxes[i].get()
            width = self.widthBoxes[i].get()
            height = self.heightBoxes[i].get()
            f.write('%s:,:%s:,:%s:,:%s:,:%s:,:%s\n' % (winName,winCmd,x,y,width,height))           
        # Close file
        f.close()
        print 'Saved window configuration to %s' % f.name 

    def moveLeft(self):
        '''Moves the selected windows to the left listbox.'''
        # Entries to move
        moveList = []
        for i in self.lb2.curselection():
            moveList.append(self.lb2.get(i))
        # Remove entries from right list boxes in backwards order
        for i in reversed(self.lb2.curselection()):
            self.lb2.delete(i)
        # Add entries to left listbox
        for entry in moveList:
            self.lb1.insert(tk.END,entry)
        # Update Entry Boxes
        self.updateEntryBoxes() 
    
    def moveRight(self):
        '''Moves the selected windows to the right listbox, to be
        saved in the configuration.'''
        # Entries to Move
        moveList = []
        for i in self.lb1.curselection():
            moveList.append(self.lb1.get(i))
        # Remove entries from left list boxes in backwards order
        for i in reversed(self.lb1.curselection()):
            self.lb1.delete(i)
        # Add entries to right listbox
        for entry in moveList:
            self.lb2.insert(tk.END,entry)
        # Update Entry Boxes
        self.updateEntryBoxes() 
    
    def setWindows(self):
        '''Sets the positions of the windows by the currently loaded configuration.'''
        pass
    
    def updateEntryBoxes(self):
        '''Updates the entry boxes with the appropriate x,y,width,height.'''
        # Update entry boxes
        num = len(self.lb2.get(0,tk.END))
        for i in range(0,self.rows-1):
            self.xBoxes[i].delete(0,tk.END)
            self.yBoxes[i].delete(0,tk.END)
            self.widthBoxes[i].delete(0,tk.END)
            self.heightBoxes[i].delete(0,tk.END)
        for i in range(0,num):
            x,y,width,height = self.getPositionSize(self.lb2.get(i))
            self.xBoxes[i].insert(0,x)
            self.yBoxes[i].insert(0,y)           
            self.widthBoxes[i].insert(0,width)
            self.heightBoxes[i].insert(0,height)
        for i in range(num,self.rows-1):
            self.cmdBoxes[i].delete(0,tk.END)

    def getPositionSize(self,windowName,show=False):
        '''Gets the size and position of a window given the window name.'''
        p = sp.Popen(["wmctrl","-l","-G"],stdout=sp.PIPE)
        out, err = p.communicate()
        mylist = out.split('\n')
        for line in mylist:
            lineu = unicode(line,'utf-8')
            if lineu.find(windowName) != -1:
                line = line.split(' ')
                line = [x for x in line if x is not '']
                x = int(line[2])
                y = int(line[3])
                width = int(line[4])
                height = int(line[5])
                
                if show:
                    print 'x: %i, y: %i, width: %i, height: %i' % (x,y,width,height)

                return x,y,width,height

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
