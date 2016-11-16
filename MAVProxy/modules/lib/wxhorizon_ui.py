import time
from wxhorizon_util import Attitude
from wx_loader import wx
import math

import matplotlib
matplotlib.use('wxAgg')
from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg as FigureCanvas
from matplotlib.figure import Figure
from matplotlib.pyplot import Polygon
import matplotlib.patheffects as PathEffects
from matplotlib import patches
import matplotlib as mpl

class HorizonFrame(wx.Frame):
    """ The main frame of the horizon indicator."""

    def __init__(self, state, title):
        self.state = state
        # Create Frame and Panel(s)
        wx.Frame.__init__(self, None, title=title)
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
        self.canvas.SetSize(wx.Size(300,300))
        self.axes.axis('off')
        self.figure.subplots_adjust(left=0,right=1,top=1,bottom=0)
        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.sizer.Add(self.canvas,1,wx.EXPAND,wx.ALL)
        self.SetSizerAndFit(self.sizer)
        self.Fit()

        # Fix Axes - vertical is of length 2, horizontal keeps the same lengthscale
        self.rescaleX()
        
        # Sky Polygon
        vertsTop = [[-1,0],[-1,1],[1,1],[1,0],[-1,0]]
        self.topPolygon = Polygon(vertsTop,facecolor='cyan',edgecolor='none')
        self.axes.add_patch(self.topPolygon)
        # Ground Polygon
        vertsBot = [[-1,0],[-1,-1],[1,-1],[1,0],[-1,0]]
        self.botPolygon = Polygon(vertsBot,facecolor='brown',edgecolor='none')
        self.axes.add_patch(self.botPolygon)
        
        # Markers
        self.axes.plot([-1,-1,1,1],[-1,1,1,-1],'ro')
        
        # Center Pointer Marker
        self.thick = 0.015
        self.axes.add_patch(patches.Rectangle((-0.75,-self.thick),0.5,2.0*self.thick,facecolor='orange',zorder=3))
        self.axes.add_patch(patches.Rectangle((0.25,-self.thick),0.5,2.0*self.thick,facecolor='orange',zorder=3))
        self.axes.add_patch(patches.Circle((0,0),radius=self.thick,facecolor='orange',edgecolor='none',zorder=3))
        
        # Pitch Markers
        self.createPitchmMarkers()
        
        # Add Roll, Pitch, Yaw Text
        self.vertSize = 0.09
        ypx = self.figure.get_size_inches()[1]*self.figure.dpi
        self.fontSize = self.vertSize*(ypx/2.0)
        leftPos = self.axes.get_xlim()[0]
        self.rollText = self.axes.text(leftPos+(self.vertSize/10.0),-0.97+(2*self.vertSize)-(self.vertSize/10.0),'Roll:   %.2f' % self.roll,color='w',size=self.fontSize)
        self.pitchText = self.axes.text(leftPos+(self.vertSize/10.0),-0.97+self.vertSize-(0.5*self.vertSize/10.0),'Pitch: %.2f' % self.pitch,color='w',size=self.fontSize)
        self.yawText = self.axes.text(leftPos+(self.vertSize/10.0),-0.97,'Yaw:   %.2f' % self.yaw,color='w',size=self.fontSize)
        
        # Show Frame
        self.Show(True)
        self.pending = []
        
    def createPitchmMarkers(self):
        '''Creates the rectangle patches for the pitch indicators.'''
        self.pitchPatches = []
        # Major Lines (multiple of 10 deg)
        for i in [-3,-2,-1,1,2,3]:
            currPatch = patches.Rectangle((-0.45,0.3*i-(self.thick/2.0)),0.9,self.thick,facecolor='w',edgecolor='none')
            self.axes.add_patch(currPatch)
            self.pitchPatches.append(currPatch)
        # Add Label for +-30 deg
        self.vertSize = 0.09
        ypx = self.figure.get_size_inches()[1]*self.figure.dpi
        self.fontSize = self.vertSize*(ypx/2.0)
        self.right30 = self.axes.text(0.5,0.9,'30',color='w',size=self.fontSize,verticalalignment='center')
        self.right30.set_path_effects([PathEffects.withStroke(linewidth=1,foreground='k')])
        self.left30 = self.axes.text(-0.5,0.9,'30',color='w',size=self.fontSize,verticalalignment='center',horizontalalignment='right')
        self.left30.set_path_effects([PathEffects.withStroke(linewidth=1,foreground='k')])
        
    def adjustPitchmarkers(self):
        '''Adjusts the location and orientation of pitch markers.'''
        rollRotate = mpl.transforms.Affine2D().rotate_deg(self.roll)+self.axes.transData
        for patch in self.pitchPatches:
            patch.set_transform(rollRotate)
        # Adjust Text Size and rotation
        self.right30.set_size(self.fontSize)
        self.left30.set_size(self.fontSize)
        self.right30.set_rotation(-self.roll)
        self.left30.set_rotation(-self.roll)
        self.right30.set_transform(rollRotate)
        self.left30.set_transform(rollRotate)

        self.right30.set_verticalalignment('center')
        self.left30.set_verticalalignment('center')
        
    def rescaleX(self):
        '''Rescales the horizontal axes to make the lengthscales equal.'''
        self.ratio = self.figure.get_size_inches()[0]/float(self.figure.get_size_inches()[1])
        self.axes.set_xlim(-self.ratio,self.ratio)
        self.axes.set_ylim(-1,1)
        
    def calcHorizonPoints(self):
        '''Updates the verticies of the patches for the ground and sky.'''
        self.ratio = self.figure.get_size_inches()[0]/float(self.figure.get_size_inches()[1])
        ydiff = math.tan(math.radians(-self.roll))*float(self.ratio)
        #pitchdiff = 
        # Sky Polygon
        vertsTop = [(-self.ratio,ydiff),(-self.ratio,1),(self.ratio,1),(self.ratio,-ydiff),(-self.ratio,ydiff)]       
        self.topPolygon.set_xy(vertsTop)
        # Ground Polygon
        vertsBot = [(-self.ratio,ydiff),(-self.ratio,-1),(self.ratio,-1),(self.ratio,-ydiff),(-self.ratio,ydiff)]       
        self.botPolygon.set_xy(vertsBot)       
        
    def updateAttitudeText(self):
        'Updates the displayed attitude Text'
        self.rollText.set_text('Roll:   %.2f' % self.roll)
        self.pitchText.set_text('Pitch: %.2f' % self.pitch)
        self.yawText.set_text('Yaw:   %.2f' % self.yaw)

    def updateRPYLocations(self):
        '''Update the locations of rol, pitch, yaw text.'''
        leftPos = self.axes.get_xlim()[0]
        # Locations
        self.rollText.set_position((leftPos+(self.vertSize/10.0),-0.97+(2*self.vertSize)-(self.vertSize/10.0)))
        self.pitchText.set_position((leftPos+(self.vertSize/10.0),-0.97+self.vertSize-(0.5*self.vertSize/10.0)))
        self.yawText.set_position((leftPos+(self.vertSize/10.0),-0.97))
        # Font Size
        ypx = self.figure.get_size_inches()[1]*self.figure.dpi
        self.fontSize = self.vertSize*(ypx/2.0)
        self.rollText.set_size(self.fontSize)
        self.pitchText.set_size(self.fontSize)
        self.yawText.set_size(self.fontSize)

    def on_idle(self, event):
        # Fix Window Scales 
        self.rescaleX()
        
        # Recalculate Horizon Polygons
        self.calcHorizonPoints()
        
        # Update Roll, Pitch, Yaw Text Locations
        self.updateRPYLocations()
        
        # Update Pitch Markers
        self.adjustPitchmarkers()
        
        # Update Matplotlib Plot
        self.canvas.draw()
        self.canvas.Refresh()
        
        
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
                
                # Recalculate Horizon Polygons
                self.calcHorizonPoints()
                
                # Update Pitch Markers
                self.adjustPitchmarkers()
                
                # Update Matplotlib Plot
                self.canvas.draw()
                self.canvas.Refresh()
                

               
                
   
        self.Refresh()
        self.Update()
