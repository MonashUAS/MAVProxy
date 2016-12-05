#!/usr/bin/env python
'''
Layout Configuration Module
Trevor Batty, November 2016

This module can save and load configurations of MAVProxy windows.
'''

from pymavlink import mavutil
import time, platform

from MAVProxy.modules.lib import mp_module
from MAVProxy.modules.lib import mp_util
from MAVProxy.modules.lib import mp_settings
from MAVProxy.modules.lib import tklayoutconfig

import subprocess as sp

class layoutConfig(mp_module.MPModule):
    def __init__(self, mpstate):
        """Initialise module"""
        super(layoutConfig, self).__init__(mpstate, "Layout Configuration", "")
        self.mpstate.layoutConfig = tklayoutconfig.LayoutConfig(mpstate=mpstate)
        
        # Check OS
        if 'Linux' not in platform.platform():
            print 'Layout Config module only works on x11 Linux based systems.'
            
    def usage(self):
        '''show help on command line options'''
        return "Usage: setup_layout: Create configruation file with GUI\nload_layout <file>: Load configuration file"

def init(mpstate):
    '''initialise module'''
    return layoutConfig(mpstate)
