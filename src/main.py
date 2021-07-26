
from m5stack_ui import *
import time
from i2c_kb import i2c_kb
from secrets import grocy_api_key, grocy_domain
from grocy_api import grocy_api

def manage_input_box(kb, textbox):
    kb.poll()
    if kb.new:
        textbox.set_text(kb.get_buffer_as_string())
        return True
    return False


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
    flag = False
    if not manage_input_box(keyboard, buffer_text):
        continue
    products = g.search_products_by_name(buffer_text.obj.get_text())
    while rows > 0:
        if manage_input_box(keyboard, buffer_text):
            flag = True
            break
        product_list.remove_label_index(0)
        rows -= 1
    if flag:
        continue
    for p in products:
        if manage_input_box(keyboard, buffer_text):
            break
        product_list.add_label(p['name'])
        rows += 1