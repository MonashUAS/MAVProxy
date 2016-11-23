#!/usr/bin/env python
'''
An example module for the confluence tutorial.
Trevor Batty, November 2016
'''

import os
import os.path
import sys
from pymavlink import mavutil
import errno
import time

from MAVProxy.modules.lib import mp_module
from MAVProxy.modules.lib import mp_util
from MAVProxy.modules.lib import mp_settings


class FLOPSexample(mp_module.MPModule):
    def __init__(self, mpstate):
        """Initialise module"""
        super(FLOPSexample, self).__init__(mpstate, "FLOPSexample", "")
        self.lowAlt = 1.0
        self.currAlt = 0.0
        self.takeoff = False
        self.warnOn = False
        self.lastWarnTime = time.time()
        self.add_command('FLOPSexample', self.cmd_altWarning, "example module", ['set','get','toggle'])

    def usage(self):
        '''show help on command line options'''
        return "Usage: example <set lowAlt|get|toggle (ON|OFF)>"

    def cmd_altWarning(self, args):
        '''control behaviour of the module'''
        if len(args) == 0:
            print self.usage()
        elif args[0] == "set":
            if len(args) == 2:
                self.setLowAlt(args[1])
            else:
                print 'Not enough arguments to set lower altitude.'
        elif args[0] == "get":
            print 'Lower altitude limit: %.f m' % self.lowAlt
        elif args[0] == 'toggle':
            if len(args) == 2:
                self.toggleWarning(args[1]) # Set from input
            elif len(args) == 1:
                self.toggleWarning(0) # Just Toggle
        else:
            print self.usage()

    def setLowAlt(self,lowAlt):
        '''Sets the lower altitude warning limit.'''
        self.lowAlt = float(lowAlt)
        print 'Lower altitude limit set to %.f m' % self.lowAlt

    def toggleWarning(self,warnOn):
        '''Toggles the warning variable.'''
        if warnOn == 'ON':
            self.warnOn = True
            print 'Lower Altitude Warning ON.'
        elif warnOn == 'OFF':
            self.warnOn = False
            print 'Lower Altitude Warning OFF.'
        else:
            self.warnOn = not self.warnOn
            if self.warnOn:
                warnstr = 'ON'
            else:
                warnstr = 'OFF'
            print 'Lower Altitude Warning %s' % warnstr 

    def mavlink_packet(self, m):
        '''handle mavlink packets'''
        if m.get_type() == 'GLOBAL_POSITION_INT':
            self.currAlt = m.relative_alt/1000.0
            # Check if we've breached the altitude on first takeoff
            if not self.takeoff:
                if self.lowAlt < self.currAlt:
                    self.takeoff = True

    def idle_task(self):
        '''called rapidly by mavproxy'''
        if (time.time() - 2.0) > self.lastWarnTime:
            if self.warnOn and self.takeoff:
                if self.currAlt < self.lowAlt:
                    print 'ALTITUDE LOW: PULL UP.'
                    self.lastWarnTime = time.time()

def init(mpstate):
    '''initialise module'''
    return FLOPSexample(mpstate)
