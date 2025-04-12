# Vehicle OBD
Supports all vehicles compliant with the OBD2 protocol.
Communication between vehicle and Raspberry Pi Zero 2W is handled by USB ELM 327 device.
A 1.8" SPI display 128x160 ST3577s has been used.

## System and Programming
Tested on Raspberry Pi Zero 2W running Raspberry Pi issued Debian 11.3
Python 3 used to execute program

## External Packages
- [Python OBD](https://python-obd.readthedocs.io/en/latest/)
- [st3577](https://pypi.org/project/st7735/)
- Python PIL

## Program Design
Object Orientated Programming used, where the display, car connection (diagnostics.py), getIps (aids connecting headlessly), metrics, commands.

Firstly, the program will continuously attempt to connect to the ELM327 adaptor and then the vehicle. Two dots will be visible on the top left of the display, the first will be red/green if not or if a ELM327 device is connected, the second dot will be red or green depending on if not or if a vehicle is connected. 
