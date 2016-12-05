MAVProxy

This is a MAVLink ground station written in python. 

Please see http://ardupilot.github.io/MAVProxy/ for more information

This ground station was developed as part of the CanberraUAV OBC team
entry

License
-------

MAVProxy is released under the GNU General Public License v3 or later

[![Gitter](https://badges.gitter.im/Join%20Chat.svg)](https://gitter.im/ArduPilot/MAVProxy?utm_source=badge&utm_medium=badge&utm_campaign=pr-badge&utm_content=badge)

Layout Config Instructions
---------------------------

This will require you have wmctrl installed, and works only with systems that use a x11 window manager. wmctrl can be installed on Ubuntu with
```
sudo apt-get update
sudo apt-get install wmctrl
```

The module can be loaded with
```
module load layoutconfig
```
This will launch a GUI which allows the windows to be configured to be selected and their relevant positions. This requires that for the first time, to create a configuration file you will need to have these windows open. The window list can be updated by clicking the Update Window List button.

![Image1](https://raw.githubusercontent.com/MonashUAS/MAVProxy/feature-layout-config/readmeImages/01.png)

To select a window to have its position and size configured, select it from the list on the left and click the >> button to move it to the right. This should display this windows current x,y position as well as its width and height. The module to load can be specified in the first entry box. For example to load the module map, which would normally require module load map, just enter map in the entry box. If nothing is to be loaded for this window then leave this blank (i.e. if you wanted to position the terminal of MAVProxy, provided that the terminal and path in terminal name is always going to be the same).

![Image2](https://raw.githubusercontent.com/MonashUAS/MAVProxy/feature-layout-config/readmeImages/02.png)

Once you are happy with the window placement and have entered the correct commands, save the config file. You should ensure that the file is correctly saved by then reloading the config file with the Load Config File button. After the first setup, this is how you will load a previous configuration file.

A sample configuration file is shown below.

```
Horizon Indicator:,:horizon:,:1920:,:52:,:960:,:1028
Map:,:map:,:2856:,:52:,:974:,:1028
Console:,:console:,:960:,:52:,:960:,:500
Mission Editor:,:misseditor:,:960:,:580:,:960:,:500

```

Clicking the Load Config File for the above configuratoin file gives the windows displayed below.

![Image3](https://raw.githubusercontent.com/MonashUAS/MAVProxy/feature-layout-config/readmeImages/03.png)

Note that for windows on the first desktop, if they overlap the title bar of the MAVProxy window, then they will be shifted slightly. This is a pain, but due to limitations of the window manager, there isn't a work around and you will just need to deal with it. Windows on the second desktop are not affected by this glitch.
