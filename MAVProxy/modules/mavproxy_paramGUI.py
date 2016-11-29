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

        param1 = ParamUpdate("TEST_PARAMETER_NAME1", "new value one")
        param2 = ParamUpdate("TEST_PARAMETER_NAME2", "new value two")
        param3 = ParamUpdate("TEST_PARAMETER_NAME3", "new value three")

        self.gui.parent_pipe_send.send(param1)
        self.gui.parent_pipe_send.send(ParamUpdateList([param2, param3]))

    def unload(self):
        '''unload module'''
        self.gui.close()

    def usage(self):
        '''show help on command line options'''
        return "Usage: "

def init(mpstate):
    '''initialise module'''
    return paramGUI(mpstate)
