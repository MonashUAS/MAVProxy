"""
  MAVProxy console

  uses lib/console.py for display
"""

from MAVProxy.modules.lib import wxhorizon
from MAVProxy.modules.lib import mp_module
from MAVProxy.modules.lib.wxhorizon_util import Attitude, VFR_HUD, Global_Position_INT, BatteryInfo, FlightState, WaypointInfo


class HorizonModule(mp_module.MPModule):
    def __init__(self, mpstate):
        # Define module load/unload reference and window title
        super(HorizonModule, self).__init__(mpstate, "horizon", "Horizon Indicator", public=True)
        self.mpstate.horizonIndicator = wxhorizon.HorizonIndicator(title='Horizon Indicator')
        self.mode = ''
        self.armed = ''
        self.currentWP = 0
        self.finalWP = 0
        self.currentDist = 0
        self.nextWPTime = 0
        self.speed = 0
        self.wpBearing = 0
        
    def unload(self):
        '''unload module'''
        self.mpstate.horizonIndicator.close()
            
    def mavlink_packet(self, msg):
        '''handle an incoming mavlink packet'''
        msgType = msg.get_type()
        master = self.master
        if msgType == 'HEARTBEAT':
            # Update state and mode information
            if type(master.motors_armed()) == type(True):
                self.armed = master.motors_armed()
                self.mode = master.flightmode
                # Send Flight State information down pipe
                self.mpstate.horizonIndicator.parent_pipe_send.send(FlightState(self.mode,self.armed))
        elif msgType == 'ATTITUDE':
            # Send attitude information down pipe
            self.mpstate.horizonIndicator.parent_pipe_send.send(Attitude(msg))
        elif msgType == 'VFR_HUD':
            # Send HUD information down pipe
            self.mpstate.horizonIndicator.parent_pipe_send.send(VFR_HUD(msg))
        elif msgType == 'GLOBAL_POSITION_INT':
            # Send altitude information down pipe
            self.mpstate.horizonIndicator.parent_pipe_send.send(Global_Position_INT(msg))
        elif msgType == 'SYS_STATUS':
            # Mode and Arm State
            self.mpstate.horizonIndicator.parent_pipe_send.send(BatteryInfo(msg))
        elif msgType in ['WAYPOINT_CURRENT', 'MISSION_CURRENT']:
            # Waypoints
            self.currentWP = msg.seq
            self.finalWP = self.module('wp').wploader.count()
            self.mpstate.horizonIndicator.parent_pipe_send.send(WaypointInfo(self.currentWP,self.finalWP,self.currentDist,self.nextWPTime,self.wpBearing))
        elif msgType == 'NAV_CONTROLLER_OUTPUT':
            self.currentDist = msg.wp_dist
            self.checkSpeed(master)
            self.nextWPTime = self.currentDist / self.speed
            self.wpBearing = msg.target_bearing
            self.mpstate.horizonIndicator.parent_pipe_send.send(WaypointInfo(self.currentWP,self.finalWP,self.currentDist,self.nextWPTime,self.wpBearing))
        
    def checkSpeed(self,master):
        # The following is borrowed from 'mavproxy_console.py'
        airspeed = master.field('VFR_HUD', 'airspeed', 30)
        if abs(airspeed - self.speed) > 5:
            self.speed = airspeed
        else:
            self.speed = 0.98*self.speed + 0.02*airspeed
        self.speed = max(1, self.speed)
        # End of borrowed section
        
def init(mpstate):
    '''initialise module'''
    return HorizonModule(mpstate)
