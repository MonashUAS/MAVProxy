#!/usr/bin/env python

"""
  MAVProxy layout configuration editor.
"""
import multiprocessing
import time

class LayoutConfig():
    '''
    Layout Configurator for MAVProxy.
    '''
    def __init__(self, title='MAVProxy: Layout Configurator'):
        self.title  = title
        
        # Create event which is fired when the GUI is closed or module unloaded
        self.close_event = multiprocessing.Event()
        self.close_event.clear()
        
        # Start GUI in another proccess
        self.child = multiprocessing.Process(target=self.child_task)
        self.child.start()

    def child_task(self):
        import tkinter as tk
        from tklayoutconfig_ui import LayoutConfigFrame
        app = tk.Tk()
    	app.title(self.title)
        app.frame = LayoutConfigFrame(state=self, mainwindow=app)
        app.mainloop()
        self.close_event.set()

    def close(self):
        '''Close the window.'''
        self.close_event.set()

    def is_alive(self):
        '''check if child is still going'''
        return self.child.is_alive()

if __name__ == "__main__":
    # test the console
    multiprocessing.freeze_support()
    layoutConfig = LayoutConfig()
    while layoutConfig.is_alive():
        print 'test'
        time.sleep(0.5)
