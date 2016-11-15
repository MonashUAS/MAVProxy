MAVProxy

This is a MAVLink ground station written in python. 

Please see http://ardupilot.github.io/MAVProxy/ for more information

This ground station was developed as part of the CanberraUAV OBC team
entry

MUAS Additions
===============

Horizon Indicator
------------------
The Horizon Indicator gives a visual indication of the current attitude of the aircraft (currently only takes into account roll).

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

![Horizon Indicator (early stages)](/MAVProxy/modules/MUAS_data/horizonIndicator.png?raw=true "Horizon Indicator (early stages)")



License
-------

MAVProxy is released under the GNU General Public License v3 or later

[![Gitter](https://badges.gitter.im/Join%20Chat.svg)](https://gitter.im/ArduPilot/MAVProxy?utm_source=badge&utm_medium=badge&utm_campaign=pr-badge&utm_content=badge)
