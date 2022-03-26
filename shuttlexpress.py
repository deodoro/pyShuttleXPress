#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Basic Contour ShuttleXpress deamon
# https://github.com/deodoro/pyShuttleXPress

__license__ = "MIT"
__version__ = "0.0.01"
__maintainer__ = "Jose Deodoro"
__email__ = "deodoro.filho@gmail.com"

import hid
import time
from pynput.mouse import Button, Controller as MouseController
from pynput.keyboard import Key, Controller as KeyboardController
import subprocess

# Initial configs
config = [("*", {"rings": {"outer": [], "inner": (["]"], ["["])}, "buttons": {0: ["keyb", Key.ctrl, 'z'], 1: ["keyb", Key.shift, Key.ctrl, 'z'], 2: [], 3: [], 4: []}})]
configs = [
    ("MyPaint", {"rings": {"inner": ([Key.ctrl, Key.left], [Key.ctrl, Key.right])}, "buttons": {0: ["keyb", Key.ctrl, 'z'], 1: ["keyb", Key.ctrl, 'y'], 2: ["mouse", Button.middle]}}),
    ("Xournal++", {"rings": {"inner": ([Key.ctrl, "-"], [Key.ctrl, "+"])}, "buttons": {0: ["keyb", Key.ctrl, 'z'], 1: ["keyb", Key.ctrl, 'y'], 2: ["mouse", Button.middle]}}),
    ("Krita", {"rings": {}, "buttons": {2: ["keyb", Key.space]}})
]

# Merge configs with the default ("*"), looking up when we receive button events is less complex this way
def merge_config(orig, new):
    global_config = [v for v in orig if v[0] == "*"]
    for key in ["rings", "buttons"]:
        for k,v in global_config[0][1][key].items():
            if k not in new[1][key]:
                new[1][key][k] = v
    return sorted([v for v in orig if v[0] != "*"] + [new], key=lambda x:x[0]) + global_config

for c in configs:
    config = merge_config(config, c)

mouse = MouseController()
keyboard = KeyboardController()

# Gets focus windows title
def GetActiveWindowTitle():
    window = subprocess.Popen(["xprop", "-root", "_NET_ACTIVE_WINDOW"], stdout=subprocess.PIPE).communicate()[0].strip().split()[-2]
    return subprocess.Popen(["xprop", "-id", window, "_NET_WM_NAME"], stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()[0].strip().split(b"\"", 1)[-1].decode("utf8")

def xor(i):
    return (i[0] or i[1]) and not (i[0] and i[1])

# If a button changed state... btn -> (button_number, 1 if down 0 if up)
def on_change_btn(btn):
    window_title = GetActiveWindowTitle()
    # print("active window=%s" % window_title)
    # find a config and simulate click/key stroke
    for item in config:
        if (item[0] in window_title or item[0] == "*") and item[1]["buttons"][btn[0]]:
            items = item[1]["buttons"][btn[0]]
            if items[0] == "keyb":
                if btn[1]:
                    for i in items[1:]:
                        keyboard.press(i)
                else:
                    for i in reversed(items[1:]):
                        keyboard.release(i)
                break
            elif items[0] == "mouse":
                if btn[1]:
                    mouse.press(items[1])
                else:
                    mouse.release(items[1])

# If a wheel changed state...
def on_change_wheel(ring, dir, idx):
    # find a config and simulate click/key stroke
    window_title = GetActiveWindowTitle()
    for item in config:
        if (item[0] in window_title or item[0] == "*") and item[1]["rings"][ring]:
            item = item[1]["rings"][ring][0 if dir > 0 else 1]
            if len(item) > 1:
                with keyboard.pressed(item[0]):
                    keyboard.tap(item[1])
                break
            else:
                keyboard.tap(item[0])
                break

# Ease speed of scrolling
def ease(t):
    return .4 * t * t * (5.0 - 2.0 * t)

if __name__ == "__main__":
    state = { "rings": { "outer": 0, "inner": 0 }, "buttons": ([False] * 5) }
    last_scroll = 0

    with hid.Device(0x0b33, 0x0020) as dev:
        # do not block, so we can send scroll events while the outer wheel is in the correct position
        dev.nonblocking = True
        while True:
            cur_state = { "outer": 0, "inner": 0 }

            r = dev.read(5)
            if r:
                btn_flags = ((r[4] << 4) | (r[3] >> 4))
                cur_state["buttons"] = [(btn_flags & (0x01 << i)) > 0 for i in range(5)]
                cur_state["rings"] = { "outer": r[0], "inner": r[1] }

                activated_btn = [(j, i[0]) for j,i in enumerate(zip(cur_state["buttons"], state["buttons"])) if xor(i)]

                for btn in activated_btn:
                    on_change_btn(btn)
                for (ring, v) in cur_state["rings"].items():
                    if v != state["rings"][ring]:
                        on_change_wheel(ring, -1 if v < state["rings"][ring] else 1, cur_state["rings"][ring])

                state = cur_state
            else:
                if state["rings"]["outer"] & 0xF0:
                    if time.time() - last_scroll > ease(1/(256 - state["rings"]["outer"])):
                        last_scroll = time.time()
                        mouse.scroll(0, -1)
                elif state["rings"]["outer"] & 0x0F:
                    if time.time() - last_scroll > ease(1/state["rings"]["outer"]):
                        last_scroll = time.time()
                        mouse.scroll(0, 1)

                time.sleep(.05)
