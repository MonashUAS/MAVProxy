#!/usr/bin/env python
'''
Graphical Parameter Editor
'''

import time
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
        self.timeout = 3   # seconds
        self.last_param_send = 0

        self.ack_list = {}
        self.fetch_list = [param_name for param_name in self.mav_param]
        self.update_list = [Param(param_name, self.mav_param[param_name]) for param_name in self.mav_param]

    def mavlink_packet(self, m):
        '''handle an incoming mavlink packet'''
        if m.get_type() == 'PARAM_VALUE':
            param_name = "%.16s" % m.param_id

            if param_name in self.ack_list:
                self.gui.pipe_module.send(ParamSendReturn(Param(param_name, m.param_value)))
                del self.ack_list[param_name]

            if not param_name in self.fetch_list:
                self.fetch_list.append(param_name)
                self.update_list.append(Param(param_name, m.param_value))

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
                    self.send_param(param.name, param.value)
            elif isinstance(obj, ParamFetch):
                self.master.param_fetch_all()
                self.fetch_list = []
                print "Fetching parameters"

        # Send new parameters to GUI if available. Rate limited to one per second to stop GUI from freezing.
        if len(self.update_list) > 0 and time.time() - self.last_param_send >= 1:
            self.last_param_send = time.time()
            self.gui.pipe_module.send(ParamUpdateList(self.update_list))
            self.update_list = []

        # Check for timed out parameters
        for param_name in self.ack_list:
            if time.time() - self.ack_list[param_name] >= self.timeout:
                print param_name + " timed out."
                del self.ack_list[param_name]
                self.gui.pipe_module.send(ParamSendFail(param_name))

    def send_param(self, name, value):
        print "Send '{0}' with value '{1}'".format(name, value)
        self.master.param_set_send(name, value)
        if not name in self.ack_list:
            self.ack_list[name] = time.time()

    def unload(self):
        '''unload module'''
        self.gui.close()

    def usage(self):
        '''show help on command line options'''
        return "Usage: "

def init(mpstate):
    '''initialise module'''
    return paramGUI(mpstate)
