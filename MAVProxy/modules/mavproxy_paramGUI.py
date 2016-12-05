#!/usr/bin/env python
'''
Graphical Parameter Editor
'''

import os.path
from MAVProxy.modules.lib import mp_module
from MAVProxy.modules.lib import tkparamGUI
from MAVProxy.modules.lib.tkparamGUI_util import *

class paramGUI(mp_module.MPModule):
    def __init__(self, mpstate):
        """Initialise module"""
        super(paramGUI, self).__init__(mpstate, "paramGUI", "Graphical Parameter Editor")
        self.mpstate = mpstate
        self.gui = tkparamGUI.ParameterEditor(vehicle_name=self.vehicle_name, title='Parameter Editor')
        self.param_file = os.path.join(self.logdir, "mav.parm")

        param_list = [Param(param_name, self.mav_param[param_name]) for param_name in self.mav_param]
        self.gui.pipe_module.send(ParamUpdateList(param_list))

    def idle_task(self):
        # Check if GUI has been closed
        if self.gui.close_event.wait(0.001):
            self.needs_unloading = True   # tell MAVProxy to unload this module
            return

        # Get messages
        while self.gui.pipe_module.poll():
            obj = self.gui.pipe_module.recv()
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
