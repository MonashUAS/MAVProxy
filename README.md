MAVProxy

This is a MAVLink ground station written in python. 

Please see http://ardupilot.github.io/MAVProxy/ for more information

This ground station was developed as part of the CanberraUAV OBC team
entry

MUAS Additions
===============

Horizon Indicator
------------------
The Horizon Indicator gives a visual indication of the current attitude of the aircraft (currently only takes into account roll), with the display and text adapting on resize of the window.

![Horizon Indicator (early stages)](/MAVProxy/modules/MUAS_data/horizonIndicator.png?raw=true "Horizon Indicator (early stages)")

To install the module, first uninstall MAVProxy using pip

```python
pip uninstall MAVProxy
```

Then download this git repository and checkout the dev branch

```python
git clone https://github.com/MonashUAS/MAVProxy.git
git checkout dev
```

Then navigate into the top level MAVProxy folder and install

```python
python setup.py build install --user
```

If it doesn't install correctly the first time, run the above command again, this should fix the problem.

### Usage
* Start up a SITL instance, see http://ardupilot.org/dev/docs/setting-up-sitl-on-linux.html
* Load the module with

```python
module load horizon
```

There are 6 main components.
* Aritifical Horizon Indicator
* Roll, Pitch, Yaw Values
* Airspeed, Altitude, Climb Rate Values
* Battery Indication
* Mode and Waypoint Information
* Heading Indication

### Artificial Horizon Indicator
The artifical horizon indicator displays the ground and sky based on the current roll angle and pitch angle of the aircraft. The distance between pitch marker lines can be changed by using the UP and DOWN arrow keys.

### Roll, Pitch, Yaw Values
Located in the bottom left corner, this displays the Roll, Pitch and Yaw angle in degrees.

### Airspeed, Altitude, Climb Rate Values
Located in the bottom right corner, this displays the airspeed (m/s), altitude above ground (m) and climb rate (m/s).

### Battery Information
The battery bar corresponds to the proportion of battery left, with the percentage displayed below the battery. If no battery information is provided, then the bar is block. NOTE: When using SITL, plane and quadplane does not provide battery information, while multirotors do. The bar is green for 51%-100% battery, 21%-50% is yellow and 0%-20% is red. The current voltage of the battery and current draw is displayed.

### Mode and Waypoint Information
Located in the top left corner, the vehicle mode is displayed in either green, for disarmed or red with a yellow outline, for armed. The current waypoint index and total number of waypoints is displayed below, while the distance and time in seconds (based purely on the distance and groundspeed) is displayed below that.

### Heading Indication
The heading indication is given by the three arrows that move around the center of the screen. The direction of the arrows are relative to the plane that is parallel to the surface of the Earth, rather than relative to the current displayed orientation by the artificial horizon indicator. The top arrow will remain in this position, and gives the current heading of the vehicle. The North point moves around the circle and points towards north, while the green pointer points to the current waypoint or point of interest, with the relative heading displayed below the pointer.

License
-------

MAVProxy is released under the GNU General Public License v3 or later

[![Gitter](https://badges.gitter.im/Join%20Chat.svg)](https://gitter.im/ArduPilot/MAVProxy?utm_source=badge&utm_medium=badge&utm_campaign=pr-badge&utm_content=badge)
