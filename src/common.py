from m5stack_ui import M5Screen
from i2c_kb import i2c_kb
from secrets import grocy_api_key, grocy_domain
from grocy_api import grocy_api
import time
import lvgl as lv
from m5stack import btnA, btnB, btnC

SCREEN_WIDTH = 320
SCREEN_HEIGHT = 240
btn_width = 80
btn_corner_radius = 20
txt_height = 32

KB_ENTRY_COMMIT_TIMEOUT_MS = 800
# Wait for this much idle time before triggering a shopping list sync
CHANGE_SYNC_MS = 5*1000
# Wait for this much idle time before triggering a full grocy sync
IDLE_SYNC_MS = 120*1000

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

def manage_input_box(kb, textbox):
    kb.poll()
    if kb.new:
        textbox.set_text(kb.get_buffer_as_string())
        return True
    return False