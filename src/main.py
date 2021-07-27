
from m5stack_ui import *
import time
from i2c_kb import i2c_kb
from secrets import grocy_api_key, grocy_domain
from grocy_api import grocy_api
import time

def manage_input_box(kb, textbox):
    kb.poll()
    if kb.new:
        textbox.set_text(kb.get_buffer_as_string())
        return True
    return False

def btn_add_cb(a, b):
    print("A: {} B: {}".format(a, b))

screen = M5Screen()
screen.clean_screen()
textarea = M5Textarea(text="Syncing with Grocy...", x=0, y=0, w=320,h=32)
g = grocy_api(grocy_api_key, grocy_domain)
g.sync()
textarea.set_text("Sync done.")
keyboard = i2c_kb(interrupt=None)

screen_width = 320
screen_height = 240
btn_width = 80
txt_height = 32
search_results = ""
screen.clean_screen()
buffer_text = M5Textarea( x=0, y=screen_height-txt_height, w=screen_width, h=txt_height)
product_list = M5List(x=0, y=0)
product_list.set_size(screen_width-btn_width,screen_height-txt_height)
btn_add = M5Btn(text="Add", x=screen_width-btn_width, y=0, w=btn_width, h=btn_width)
btn_add.set_cb(btn_add_cb)

print("Looping")
keyboard.new = True
products = []
displayed = {}
while True:
    t = time.ticks_ms()
    flag = False
    while time.ticks_diff(time.ticks_ms(), t) < 1000 or not flag:
        if manage_input_box(keyboard, buffer_text):
            # If a button is pressed, restart the timer.
            flag = True
            t = time.ticks_ms()

    # Things have been set in motion...
    products = list(g.search_product_names_by_name(buffer_text.obj.get_text()))
    to_remove_from_displayed = []
    for disp in displayed:
        if disp not in products:
            i = product_list.get_label_index(displayed[disp])
            product_list.remove_label_index(i)
            to_remove_from_displayed.append(disp)
        else:
            products.remove(disp)
    for product in products:
        displayed[product] = product_list.add_label(product)
    for disp in to_remove_from_displayed:
        del displayed[disp]