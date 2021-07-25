
from m5stack_ui import *
import time
from i2c_kb import i2c_kb
from secrets import grocy_api_key, grocy_domain
from grocy_api import grocy_api
import micropython
micropython.alloc_emergency_exception_buf(100)

screen = M5Screen()
screen.clean_screen()
textarea = M5Textarea()

print("API Initialising")
g = grocy_api(grocy_api_key, grocy_domain)
print("Starting sync")
# g.sync()
print("Sync done")
keyboard = i2c_kb(interrupt=None)

search_results = ""

print("Looping")
while True:
    keyboard.poll()
    if keyboard.new:
        buffer = keyboard.get_buffer_as_string()
        print("Got keyboard buffer: {}".format(buffer))
        # textarea.set_text(buffer)
        search_results = ""
        print("Looking for products")
        for product in g.search_products_by_name(buffer):
            search_results += product['name'] + "\n"
        print("Writing results to textarea: {}".format(search_results))
        # screen.clean_screen()
        # textarea = M5Textarea()
        textarea.set_text(search_results)
    # time.sleep(0.1)



# def keyboard_cb(value):
#   print("Key value:", end='')
#   print(value)

# print("Looping")
# while True:
#   time.sleep(0.1)
#   textarea.set_text(keyboard.get_buffer_as_string())

# keyboard.callback(keyboard_cb)