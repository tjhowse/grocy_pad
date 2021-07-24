
from m5stack_ui import *
import time
from i2c_kb import i2c_kb
from secrets import grocy_api_key, grocy_domain
# from grocy_api import grocy_api

screen = M5Screen()
screen.clean_screen()
textarea = M5Textarea()

# print("API Initialising")
# g = grocy_api(grocy_api_key, grocy_domain)
# print("Starting sync")
# g.sync()
# print("Sync done")
# for product in g.search_products_by_name('sugar'):
#     print(product['name'])
# print("Print done")

keyboard = i2c_kb()

search_term = ""

# def keyboard_cb(value):
#   print("Key value:", end='')
#   print(value)

# print("Looping")
# while True:
#   time.sleep(0.1)
#   textarea.set_text(keyboard.get_buffer_as_string())

# keyboard.callback(keyboard_cb)