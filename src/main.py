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

def btn_add_cb(obj, event):
    if event == lv.EVENT.CLICKED:
        # TODO check the label. It should change to "Remove" or something
        # if we've selected a product in the shopping list.
        global selected_product
        global shopping_list
        global btn_add_label
        if btn_add_label.get_text() == "Add":
            shopping_list.add(selected_product)
        else:
            shopping_list.remove(selected_product)

def product_list_cb(obj, event):
    list_btn = lv.list.__cast__(obj)
    if event == lv.EVENT.CLICKED:
        # TODO Put all this into its own class and use class member references rather than globals
        global selected_product
        global shopping_list
        selected_product = list_btn.get_btn_text()
        if selected_product in shopping_list:
            btn_add_label.set_text("Remove")
        else:
            btn_add_label.set_text("Add")

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

shopping_list = set(g.get_shopping_list())

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
btn_add.set_event_cb(btn_add_cb)
btn_add_label = lv.label(btn_add)
btn_add_label.set_text("Add")


on_shopping_list_colour = lv.color_make(255,255,255)
selected_product = ""

print("Looping")
keyboard.new = True
products = []
displayed = {}
while True:
    t = time.ticks_ms()
    flag = False
    while time.ticks_diff(time.ticks_ms(), t) < 800 or not flag:
        if manage_input_box(keyboard, buffer_text):
            # If a button is pressed, restart the timer.
            flag = True
            t = time.ticks_ms()
    print(selected_product)
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
        displayed[product].set_event_cb(product_list_cb)
    for disp in to_remove_from_displayed:
        displayed.pop(disp)
    # Highlight items in the shopping list.
    for p in displayed:
        if p in shopping_list:
            displayed[p].set_style_local_bg_color(0, 0, lv.color_make(128,255,128))
        else:
            displayed[p].set_style_local_bg_color(0, 0, lv.color_make(255,255,255))