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
    def __init__(self, title='MAVProxy: Parameter Editor'):
        self.title  = title
        # Create Pipe to send attitude information from module to UI
        self.pipe_gui, self.pipe_mavproxy = multiprocessing.Pipe(duplex=True)
        #self.child_pipe_recv, self.parent_pipe_send = multiprocessing.Pipe(duplex=False)
        self.close_event = multiprocessing.Event()
        self.close_event.clear()
        self.child = multiprocessing.Process(target=self.child_task)
        self.child.start()
        self.pipe_gui.close()

    def child_task(self):
        self.pipe_mavproxy.close()

        import tkinter as tk
        from tkparamGUI_ui import ParamGUIFrame
        app = tk.Tk()
    	app.title(self.title)
        app.frame = ParamGUIFrame(state=self, mainwindow=app)
        app.mainloop()

    def close(self):
        '''Close the window.'''
        self.close_event.set()
        if self.is_alive():
            self.child.join(2)

    def is_alive(self):
        '''check if child is still going'''
        return self.child.is_alive()

if __name__ == "__main__":
    # test the console
    multiprocessing.freeze_support()
    paramGUI = ParameterEditor()
    while paramGUI.is_alive():
        print 'test'
        time.sleep(0.5)
