
from m5stack_ui import *
import time
from i2c_kb import i2c_kb
from secrets import ssid, password

import wifiCfg

wifiCfg.doConnect(ssid, password)

screen = M5Screen()
screen.clean_screen()
textarea = M5Textarea()

keyboard = i2c_kb()

def keyboard_cb(value):
  print("Key value:", end='')
  print(value)

keyboard.callback(keyboard_cb)