"""
  MAVProxy console

  uses lib/console.py for display
"""

import os, sys, math, time
import multiprocessing

from MAVProxy.modules.lib import wxhorizon
from MAVProxy.modules.lib import textconsole
from MAVProxy.modules.mavproxy_map import mp_elevation
from pymavlink import mavutil
from MAVProxy.modules.lib import mp_util
from MAVProxy.modules.lib import mp_module
from MAVProxy.modules.lib import wxsettings

class HorizonModule(mp_module.MPModule):
    def __init__(self, mpstate):
        # Define module load/unload reference and window title
        super(HorizonModule, self).__init__(mpstate, "horizon", "Horizon Indicator", public=True)
        self.mpstate.horizonIndicator = wxhorizon.HorizonIndicator(title='Horizon Indicator')
        
        # Pipe to send information
        self.parent_pipe,self.child_pipe = multiprocessing.Pipe()
        
        self.pitch = 0

    def unload(self):
        '''unload module'''
        self.mpstate.horizonIndicator.close()

    def updatePitch(self):
        '''Sends updated pitch to GUI'''
        if self.child.is_alive():
            self.parent_pipe.send(self.pitch)

    def mavlink_packet(self, msg):
        '''handle an incoming mavlink packet'''
        if msg.get_type() == 'ATTITUDE':
            self.pitch = msg.pitch
            print self.pitch

def init(mpstate):
    '''initialise module'''
    return HorizonModule(mpstate)
