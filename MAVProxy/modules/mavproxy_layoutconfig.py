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
        self.mpstate.layoutcConfig = tklayoutconfig.LayoutConfig()
        


        self.add_command('listwins', self.cmd_getWindowList, "Layout Configuration Module")
        self.add_command('getwingeo', self.cmd_getPositionSize, "Layout Configuration Module")

        
        # wmctrl -r "Horizon Indicator" -e 1,200,100,800,400 -b remove,maximized_horz,maximized_vert
        # wmctrl -l -G
        
        
        
        # Check OS
        if not (platform.platform()).contains('Linux'):
            print 'Layout Config module only works on x11 Linux based systems.'
            
    def usage(self):
        '''show help on command line options'''
        return "Usage: example <status|set>"

    def cmd_example(self,args):
        '''control behaviour of the module'''
        if len(args) == 0:
            print self.usage()
        elif args[0] == "status":
            print self.status()
        elif args[0] == "set":
            self.example_settings.command(args[1:])
        else:
            print self.usage()

    def cmd_getWindowList(self,args):
        '''Gets the window list for the long names of windows.'''
        p = sp.Popen(["wmctrl","-l"],stdout=sp.PIPE)
        out, err = p.communicate()
        mylist = out.split('\n')
        winNames = []
        for line in mylist:
            if len(line)>0:
                line = line.split(' ')
                thisLine = " ".join(line[4:])
                winNames.append(thisLine)
                print thisLine
        
        return winNames
    
    def cmd_getPositionSize(self,args):
        '''Gets the size and position of a window given the window name.'''
        p = sp.Popen(["wmctrl","-l","-G"],stdout=sp.PIPE)
        out, err = p.communicate()
        mylist = out.split('\n')
        windowName = args[0]
        print windowName
        for line in mylist:
            if line.find(windowName) != -1:
                line = line.split(' ')
                x = int(line[3])
                y = int(line[4])
                width = int(line[5])
                height = int(line[6])
                
                print 'x: %i, y: %i, width: %i, height: %i' % (x,y,width,height)

                return x,y,width,height
        

    def mavlink_packet(self, m):
        '''handle mavlink packets'''
        if m.get_type() == 'GLOBAL_POSITION_INT':
            if self.settings.target_system == 0 or self.settings.target_system == m.get_srcSystem():
                self.packets_mytarget += 1
            else:
                self.packets_othertarget += 1

def init(mpstate):
    '''initialise module'''
    return layoutConfig(mpstate)
