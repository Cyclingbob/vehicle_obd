# Vehicle OBD
Supports all vehicles compliant with the OBD2 protocol.
Communication between vehicle and Raspberry Pi Zero 2W is handled by USB ELM 327 device.
A 1.8" SPI display 128x160 ST3577s has been used.

## System and Programming
Tested on Raspberry Pi Zero 2W running Raspberry Pi issued Debian 11.3
Python 3 used to execute program

## Branches
Dev branch contains an unstable but much newer version of code. Once this has been adequately tested, this will be merged into main. Use `git checkout dev` to change between branches after you've cloned this repository.

## Virtual Environment
Due to frustrating changes with newer versions of debian, you may need to use virtual environments to correctly run the program
`cd vehicle_obd`, then `python -m venv obd_venv`, then `source obd_venv/bin/activate`.
This will "activate" the virtual environment. Run `python3 main.py` and `python3 -m pip install <package>` as usual:

## External Packages
- [Python OBD](https://python-obd.readthedocs.io/en/latest/) (pip install obd)
- [st3577](https://pypi.org/project/st7735/) (pip install st7735)
- Python PIL (pip install pillow)
- gpiod (pip install gpiod)
- gpiodevice (pip install gpiodevice)
- [Flask](https://flask.palletsprojects.com/en/stable/) (pip install flask)

## Execution
`python3 main.py`

## Program Design
Object Orientated Programming used, where the display, car connection (diagnostics.py), getIps (aids connecting headlessly), metrics, commands.

Firstly, the program will continuously attempt to connect to the ELM327 adaptor and then the vehicle. Two dots will be visible on the top left of the display, the first will be red/green if not or if a ELM327 device is connected, the second dot will be red or green depending on if not or if a vehicle is connected. 
