import time
import os
import mp_menu
from wxconsole_util import Value, Text
from wx_loader import wx

class HorizonFrame(wx.Frame):
    """ The main frame of the console"""

    def __init__(self, state, title):
        self.state = state
        # Create Frame and Panel
        wx.Frame.__init__(self, None, title=title, size=(400,400))
        self.panel = wx.Panel(self)
        state.frame = self

        # Create vbox and panel
        self.vbox = wx.BoxSizer(wx.VERTICAL)
        self.panel.SetSizer(self.vbox)

        # Create Event Timer
        self.timer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.on_timer, self.timer)
        self.timer.Start(100)
        self.Bind(wx.EVT_IDLE, self.on_idle)

        # Test Button
        self.btn = wx.Button(self.panel,-1,'Display Pitch')
        self.vbox.Add(self.btn,0,wx.ALIGN_CENTER)
        self.Bind(wx.EVT_BUTTON,self.OnButtonClicked)

        self.pitch = 0

        # Show Window
        self.Show(True)
        self.pending = []

    def OnButtonClicked(self,e):
        print 'Pitch: %f.' % self.pitch
        e.Skip()

    def on_idle(self, event):
        time.sleep(0.05)

    def on_timer(self, event):
        state = self.state
        if state.close_event.wait(0.001):
            self.timer.Stop()
            self.Destroy()
            return
   
        self.Refresh()
        self.Update()