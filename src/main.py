from m5stack_ui import M5Screen
import time
from i2c_kb import i2c_kb
from secrets import grocy_api_key, grocy_domain
from grocy_api import grocy_api
import time
import lvgl as lv

SCREEN_WIDTH = 320
SCREEN_HEIGHT = 240
btn_width = 80
btn_corner_radius = 20
txt_height = 32

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

shopping_list = list(g.get_shopping_list())

spinner.delete()
msg.delete()
show_msg("Sync done")

keyboard = i2c_kb(interrupt=None)

search_results = ""
scr.clean()
buffer_text = lv.textarea(scr)
buffer_text.set_width(SCREEN_WIDTH)
buffer_text.set_height(txt_height)
buffer_text.align(None, lv.ALIGN.IN_BOTTOM_LEFT, 0, 0)
product_list = lv.list(scr)
product_list.set_size(SCREEN_WIDTH-btn_width, SCREEN_HEIGHT-txt_height)
product_list.align(None, lv.ALIGN.IN_TOP_LEFT, 0, 0)
btn_add = lv.btn(scr)
btn_add.set_width(btn_width)
btn_add.set_height(btn_width)
btn_add.set_style_local_radius(lv.btn.PART.MAIN,lv.STATE.DEFAULT,btn_corner_radius)
btn_add.align(None, lv.ALIGN.IN_TOP_RIGHT, 0,0)
btn_add_label = lv.label(btn_add)
btn_add_label.set_text("Add")


on_shopping_list_colour = lv.color_make(255,255,255)

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
    products = list(g.search_product_names_by_name(buffer_text.get_text()))
    to_remove_from_displayed = []
    for disp in displayed:
        if disp not in products:
            i = product_list.get_btn_index(displayed[disp])
            product_list.remove(i)
            to_remove_from_displayed.append(disp)
        else:
            products.remove(disp)
    for product in products:
        displayed[product] = product_list.add_btn(None, product)
        if product in shopping_list:
            displayed[product].set_style_local_bg_color(0, 0, lv.color_make(128,255,128))
    for disp in to_remove_from_displayed:
        del displayed[disp]