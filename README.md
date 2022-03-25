# pyShuttleXPress
 A simple Contour ShuttleXPress deamon written in python

# What is it

It is [device with a jog wheel and shortcut buttons](https://www.contourdesign.com/product/shuttle/#) that I use as companion for my Wacom tablet/monitor.

Windows and mac drivers works fine. Linux support is not as great but it's decent, there are several options. [This dude](https://github.com/EMATech/ContourShuttleXpress) did an awesome job on gathering information and writing a nice UI in Python.

I wanted/needed something simpler, this is it. I basically don't like the way people implement the outer wheel, I wanted a eased-in-out scroll button, and it to accellerate when pushed to the extreme (most drivers use each step as a scroll commmand).

# How it works

I cannot do better than @rdoursenaud (above), he put serious effort on documentation and comments. This code follows the same protocols: once it's setup in UDEV, each action will deliver a 5 byte packet, the code unpacks and calls mouse/keyboard simulation using pynput, depending on a configured array.

# To get started

Install dependencies:

    pip install -r requirements.txt

Configure UDEV (works on Arch and Ubuntu, might be different for other distros):

    sudo cp 90-shuttlexpress.rules /etc/udev/rules.d
    sudo udevadm control --reload-rules

Run as SUDO:

    python shuttlexpress.py

# Todo

* Write the config in JSON and load;
* Startup as a service;
* Logging.
* Refactor contants and hacks
