#!/usr/bin/env python

"""
  MAVProxy graphical parameter editor.
"""
import multiprocessing
import time

class ParameterEditor():
    '''
    Graphical parameter editor for MAVProxy.
    '''
    def __init__(self, vehicle_name="ArduPlane", title="MAVProxy: Parameter Editor"):
        self.title  = title
        self.vehicle_name = vehicle_name

        # Create pipe to send information between module and GUI
        self.pipe_gui, self.pipe_module = multiprocessing.Pipe(duplex=True)

        # Create event which is fired when the GUI is closed or module unloaded
        self.close_event = multiprocessing.Event()
        self.close_event.clear()

        # Start GUI in another proccess
        self.child = multiprocessing.Process(target=self.child_task)
        self.child.start()

        # Don't allow module to send from pipe_gui
        self.pipe_gui.close()

    def child_task(self):
        # Don't allow GUI to send from pipe_module
        self.pipe_module.close()

        # Create app window
        try:
            import tkinter as tk
        except:
            import Tkinter as tk
        from tkparamGUI_ui import ParamGUIFrame
        app = tk.Tk()
    	app.title(self.title)
        app.frame = ParamGUIFrame(state=self, mainwindow=app)
        app.mainloop()
        self.close_event.set()   # indicate that the GUI has closed

    def close(self):
        '''Close the window.'''
        self.close_event.set()
        if self.is_alive():
            self.child.join(2)

    def is_alive(self):
        '''check if child is still going'''
        return self.child.is_alive()

if __name__ == "__main__":
    multiprocessing.freeze_support()
    paramGUI = ParameterEditor()
    while paramGUI.is_alive():
        print 'test'
        time.sleep(0.5)
