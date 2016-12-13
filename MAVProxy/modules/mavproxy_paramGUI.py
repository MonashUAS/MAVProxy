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
        self.add_command('paramGUI', self.cmd_param, "graphical parameter editor",
                         ["fav <set|add|remove> (PARAMETER_LIST)"])

        self.mpstate = mpstate
        self.gui = None
        self.param_file = os.path.join(self.logdir, "mav.parm")
        self.timeout = 3   # seconds

        self.last_send = -1
        self.send_list = []

        # Save favorites set in mpstate so it can be updated even when the module isn't loaded.
        try:
            self.send_msg(FavSet(self.mpstate.paramGUI_fav_set))
        except AttributeError:
            self.mpstate.paramGUI_fav_set = set()

        self.ack_list = {}
        self.fetch_list = [param_name for param_name in self.mav_param]
        self.send_msg([ParamUpdate(Param(param_name, self.mav_param[param_name])) for param_name in self.mav_param])

    def mavlink_packet(self, m):
        '''handle an incoming mavlink packet'''
        if m.get_type() == 'PARAM_VALUE':
            param_name = "%.16s" % m.param_id

            if not param_name in self.fetch_list:
                self.fetch_list.append(param_name)

            if param_name in self.ack_list:
                self.send_msg(ParamSendReturn(Param(param_name, m.param_value)))
                del self.ack_list[param_name]
                return

            self.send_msg(ParamUpdate(Param(param_name, m.param_value)))

    def idle_task(self):
        # Wait for vehicle_name to be set before loading the gui
        if self.gui == None:
            if self.mpstate.vehicle_name != None:
                self.gui = tkparamGUI.ParameterEditor(vehicle_name=self.vehicle_name, title='Parameter Editor')
            return

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

        # Send new messages to GUI if available. Rate limited to one batch per second to stop GUI from freezing.
        if len(self.send_list) > 0 and time.time() - self.last_send >= 1:
            self.last_send = time.time()
            self.gui.pipe_module.send(self.send_list)
            self.send_list = []

        # Check for timed out parameters
        for param_name in self.ack_list:
            if time.time() - self.ack_list[param_name] >= self.timeout:
                print param_name + " timed out."
                del self.ack_list[param_name]
                self.send_msg(ParamSendFail(param_name))

    def cmd_param(self, args):
        usage = "Usage: paramGUI <fav>"
        if len(args) < 1:
            print usage
            return
        if args[0] == "fav":
            fav_usage = "Usage: paramGUI fav <set|add|remove> (PARAMETER_LIST)\nPARAMETER_LIST is a comma seperated list with no spaces (e.g. ARMING_CHECK,AHRS_ORIENTATION,ALT_MIX)"
            if len(args) != 3:
                print fav_usage
                return

            param_set = set([param.upper() for param in args[2].split(",")]) - set([""])
            if args[1] == "set":
                self.mpstate.paramGUI_fav_set = param_set
            elif args[1] == "add":
                self.mpstate.paramGUI_fav_set |= param_set
            elif args[1] == "remove":
                self.mpstate.paramGUI_fav_set -= param_set
            else:
                print fav_usage
                return
            
            self.send_msg(FavSet(self.mpstate.paramGUI_fav_set))
        else:
            print usage

    def send_msg(self, msg):
        if isinstance(msg, list):
            self.send_list += msg
        else:
            self.send_list.append(msg)

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
