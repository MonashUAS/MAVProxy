#!/usr/bin/env python
'''
Graphical Parameter Editor
'''

from MAVProxy.modules.lib import mp_module
from MAVProxy.modules.lib import tkparamGUI
from MAVProxy.modules.lib.tkparamGUI_util import *

class paramGUI(mp_module.MPModule):
    def __init__(self, mpstate):
        """Initialise module"""
        super(paramGUI, self).__init__(mpstate, "paramGUI", "Graphical Parameter Editor")
        self.mpstate = mpstate
        self.gui = tkparamGUI.ParameterEditor(title='Parameter Editor')

        param1 = Param("TEST_PARAMETER_NAME1", "new value one")
        param2 = Param("TEST_PARAMETER_NAME2", "new value two")
        param3 = Param("TEST_PARAMETER_NAME3", "new value three")

        self.gui.pipe_mavproxy.send(ParamUpdateList([param1, param2, param3]))

    def idle_task(self):
        if self.gui.close_event.wait(0.001):
            self.mainwindow.destroy()
            return
        # Get messages
        while self.gui.pipe_mavproxy.poll():
            obj = self.gui.pipe_mavproxy.recv()
            if isinstance(obj, ParamSendList):
                for param in obj.params:
                    print "Send '{0}' with value '{1}'.".format(param.name, param.value)
            elif isinstance(obj, ParamFetch):
                print "Fetch parameters"

    def unload(self):
        '''unload module'''
        self.gui.close()

    def usage(self):
        '''show help on command line options'''
        return "Usage: "

def init(mpstate):
    '''initialise module'''
    return paramGUI(mpstate)
