
from m5stack_ui import *
import time
from i2c_kb import i2c_kb
from secrets import grocy_api_key, grocy_domain
from grocy_api import grocy_api

def manage_input_box(kb, textbox):
    kb.poll()
    if kb.new:
        textbox.setText(kb.get_buffer_as_string())

# return
screen = M5Screen()
screen.clean_screen()
textarea = M5Textarea(text="Syncing with Grocy...", x=0, y=0, w=320,h=32)
g = grocy_api(grocy_api_key, grocy_domain)
g.sync()
textarea.set_text("Sync done.")
keyboard = i2c_kb(interrupt=None)

search_results = ""
screen.clean_screen()
buffer_text = M5Textarea( x=0, y=240-32, w=320, h=32)
product_list = M5List(x=0, y=0)
product_list.set_size(260,240-32)
rows = 0

print("Looping")
keyboard.new = True
while True:
    keyboard.poll()
    if keyboard.new:
        buffer = keyboard.get_buffer_as_string()
        buffer_text.set_text(buffer)
        while rows > 0:
            product_list.remove_label_index(0)
            rows -= 1
        # product_list = M5List(x=0, y=0)
        # product_list.set_size(260,240-32)
        for product in g.search_products_by_name(buffer):
            product_list.add_label(product['name'])
            rows += 1
            # pass

    # time.sleep(0.1)



# def keyboard_cb(value):
#   print("Key value:", end='')
#   print(value)

# print("Looping")
# while True:
#   time.sleep(0.1)
#   textarea.set_text(keyboard.get_buffer_as_string())

# keyboard.callback(keyboard_cb)