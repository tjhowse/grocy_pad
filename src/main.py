
from m5stack_ui import *
import time
from i2c_kb import i2c_kb


screen = M5Screen()
screen.clean_screen()
textarea = M5Textarea()

keyboard = i2c_kb()

# read once
print("Key value:", end='')
print(keyboard.read())

# callback
def keyboard_cb(value):
  print("Key value:", end='')
  print(value)

keyboard.callback(keyboard_cb)
# while True:
#     time.sleep(0.1)
#     a = keyboard.read()
#     if a != b'\x00':
#         print(a)