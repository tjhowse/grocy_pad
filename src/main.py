from m5stack_ui import M5Screen
import time
from i2c_kb import i2c_kb
from secrets import grocy_api_key, grocy_domain
from grocy_api import grocy_api
import time
import lvgl as lv

def manage_input_box(kb, textbox):
    kb.poll()
    if kb.new:
        textbox.set_text(kb.get_buffer_as_string())
        return True
    return False

def btn_add_cb(a, b):
    # print("A: {} B: {}".format(a, b))
    if b == 0:
        # Touch down
        pass

def show_msg(msg, x = 0, y = 0):
    box = lv.msgbox(lv.scr_act())
    box.set_text(msg)
    box.align(None, lv.ALIGN.IN_TOP_MID, 0, 0)
    return box

def show_spinner():
    preload = lv.spinner(lv.scr_act(), None)
    preload.set_size(100, 100)
    preload.align(None, lv.ALIGN.CENTER, 0, 0)
    return preload

screen = M5Screen()

scr = lv.scr_act()
scr.clean()
msg = show_msg("Syncing with Grocy...", 10, 10)
spinner = show_spinner()

g = grocy_api(grocy_api_key, grocy_domain)
g.sync()

spinner.delete()
msg.delete()
show_msg("Sync done")

keyboard = i2c_kb(interrupt=None)

screen_width = 320
screen_height = 240
btn_width = 80
txt_height = 32
search_results = ""
scr.clean()
buffer_text = lv.textarea(scr)
buffer_text.align(None, lv.ALIGN.IN_BOTTOM_MID, 0, 0)
# buffer_text.set_x(0)
# buffer_text.set_y(screen_height-txt_height)
# buffer_text.set_width(screen_width)
# buffer_text.set_height(txt_height)
product_list = lv.list(scr)
product_list.align(None, lv.ALIGN.IN_TOP_MID, 0, 0)
# product_list.set_size(screen_width-btn_width,screen_height-txt_height)
# btn_add = M5Btn(text="Add", x=screen_width-btn_width, y=0, w=btn_width, h=btn_width)
# btn_add.set_cb(btn_add_cb)

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