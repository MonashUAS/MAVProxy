#!/usr/bin/env python

"""
  MAVProxy message console, implemented in a child process
"""
import multiprocessing, threading
import textconsole, sys, time

class HorizonIndicator():
    '''
    a message console for MAVProxy
    '''
    def __init__(self,title='MAVProxy: Horizon Indicator'):
        self.title  = title
        self.close_event = multiprocessing.Event()
        self.close_event.clear()
        self.child = multiprocessing.Process(target=self.child_task)
        self.child.start()
        #t = threading.Thread()
        #t.daemon = True
        #t.start()

    def child_task(self):
        '''child process - this holds all the GUI elements'''
        import wx_processguard
        from wx_loader import wx
        from wxhorizon_ui import HorizonFrame
        # Create wx application
        app = wx.App(False)
        app.frame = HorizonFrame(state=self, title=self.title)
        app.frame.SetDoubleBuffered(True)
        app.frame.Show()
        app.MainLoop()


    def close(self):
        '''close the console'''
        self.close_event.set()
        if self.is_alive():
            self.child.join(2)

    def is_alive(self):
        '''check if child is still going'''
        return self.child.is_alive()

if __name__ == "__main__":
    # test the console
    multiprocessing.freeze_support()
    horizon = HorizonIndicator()
    while horizon.is_alive():
        print 'test'
        time.sleep(0.5)
