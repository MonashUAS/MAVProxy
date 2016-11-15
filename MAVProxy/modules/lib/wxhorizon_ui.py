import time
from wxhorizon_util import Attitude
from wx_loader import wx
import math

import matplotlib
matplotlib.use('wxAgg')
from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg as FigureCanvas
from matplotlib.figure import Figure
from matplotlib.pyplot import Polygon

class HorizonFrame(wx.Frame):
    """ The main frame of the horizon indicator."""

    def __init__(self, state, title):
        self.state = state
        # Create Frame and Panel(s)
        wx.Frame.__init__(self, None, title=title, size=(400,400))
        state.frame = self

        # Initialisation
        self.initData()
        self.initUI()


    def initData(self):
        # Initialise Attitude
        self.pitch = 0  # Degrees
        self.roll = 0   # Degrees
        self.yaw = 0    # Degrees
        
        # History Values
        self.oldRoll = 0 # Degrees
    

    def initUI(self):
        # Create Event Timer
        self.timer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.on_timer, self.timer)
        self.timer.Start(100)
        self.Bind(wx.EVT_IDLE, self.on_idle)

        # Create Panel
        self.panel = wx.Panel(self)
        
        # Create Matplotlib Panel
        self.figure = Figure()
        self.axes = self.figure.add_subplot(111)
        self.canvas = FigureCanvas(self,-1,self.figure)
        self.axes.axis('off')
        self.figure.subplots_adjust(left=0,right=1,top=1,bottom=0)
        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.sizer.Add(self.canvas,1,wx.LEFT|wx.TOP|wx.GROW)
        self.SetSizer(self.sizer)
        self.Fit()
        
        # Fix Axes - vertical is of length 2, horizontal keeps the same lengthscale
        ratio = self.GetSize()[0]
        self.axes.set_xlim(-1,1)
        self.axes.set_ylim(-1,1)
        
        # Horizon setup
        # Sky Polygon
        vertsTop = [[-1,0],[-1,1],[1,1],[1,0],[-1,0]]
        self.topPolygon = Polygon(vertsTop,facecolor='cyan',edgecolor='none')
        self.axes.add_patch(self.topPolygon)
        # Ground Polygon
        vertsBot = [[-1,0],[-1,-1],[1,-1],[1,0],[-1,0]]
        self.botPolygon = Polygon(vertsBot,facecolor='brown',edgecolor='none')
        self.axes.add_patch(self.botPolygon)
        
  
        
        # Show Frame
        self.Show(True)
        self.pending = []
        
        
    def calcHorizonPoints(self):
        '''Updates the verticies of the patches for the ground and sky.'''
        ydiff = math.sin(math.radians(self.roll))
        # Sky Polygon
        vertsTop = [(-1,ydiff),(-1,1),(1,1),(1,-ydiff),(-1,ydiff)]       
        self.topPolygon.set_xy(vertsTop)
        # Ground Polygon
        vertsBot = [(-1,ydiff),(-1,-1),(1,-1),(1,-ydiff),(-1,ydiff)]       
        self.botPolygon.set_xy(vertsBot)       
        
        
    def updateAttitudeText(self):
        'Updates the displayed attitude Text'
        #self.pitchText.SetLabel('Pitch: %.2f' % self.pitch)
        #self.rollText.SetLabel('Roll: %.2f' % self.roll)
        #self.yawText.SetLabel('Yaw: %.2f' % self.yaw)

    def on_idle(self, event):
        time.sleep(0.05)
 
    def on_timer(self, event):
        state = self.state
        if state.close_event.wait(0.001):
            self.timer.Stop()
            self.Destroy()
            return
        # Get attitude information
        while state.child_pipe_recv.poll():
            obj = state.child_pipe_recv.recv()
            if isinstance(obj,Attitude):
                self.oldRoll = self.roll
                self.pitch = obj.pitch*180/math.pi
                self.roll = obj.roll*180/math.pi
                self.yaw = obj.yaw*180/math.pi
                
                # Update Displayed Text
                self.updateAttitudeText()
                self.calcHorizonPoints()
                
                # Update Matplotlib Plot
                self.canvas.draw()
                self.canvas.Refresh()
                
   
        self.Refresh()
        self.Update()