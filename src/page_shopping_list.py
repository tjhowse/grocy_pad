from common import *

class page_shopping_list:
    def btn_add_cb(self, obj, event):
        if event == lv.EVENT.CLICKED:
            if not self.selected_product:
                return
            if self.btn_add_label.get_text() == "Add":
                self.shopping_list.add(self.selected_product)
            else:
                self.shopping_list.remove(self.selected_product)
            self.selected_product = ""
            self.btn_add_label.set_text("Add")
            self.shopping_list_changed = True
            self.highlight_products_on_shopping_list()

    def btn_view_cb(self, obj, event):
        if event == lv.EVENT.CLICKED:
            if self.mode == "browse":
                self.mode = "view"
                self.btn_view_label.set_text("Browse")
            else:
                self.mode = "browse"
                self.btn_view_label.set_text("View\nList")
            self.reset_entry_state()

    def btn_clear_cb(self, obj, event):
        if event == lv.EVENT.CLICKED:
            self.reset_entry_state()

    def product_list_cb(self, obj, event):
        if event == lv.EVENT.CLICKED:
            list_btn = lv.list.__cast__(obj)
            self.selected_product = list_btn.get_btn_text()
            if self.selected_product in self.shopping_list:
                self.btn_add_label.set_text("Remove")
            else:
                self.btn_add_label.set_text("Add")

    def reset_entry_state(self):
        self.buffer_text.set_text("")
        self.selected_product = ""
        self.keyboard.clear_buffer()
        self.keyboard.new = True

    def __init__(self, grocy):
        self.g = grocy
        scr = lv.scr_act()
        scr.clean()

        self.shopping_list = set(self.g.get_shopping_list())
        self.keyboard = i2c_kb(interrupt=None)
        self.selected_product = ""
        self.mode = "browse"
        self.shopping_list_changed = False

        self.buffer_text = lv.textarea(scr)
        self.buffer_text.set_width(SCREEN_WIDTH)
        self.buffer_text.set_height(txt_height)
        self.buffer_text.align(None, lv.ALIGN.IN_BOTTOM_LEFT, 0, 0)
        self.product_list = lv.list(scr)
        self.product_list.set_size(SCREEN_WIDTH-btn_width, SCREEN_HEIGHT-txt_height)
        self.product_list.align(None, lv.ALIGN.IN_TOP_LEFT, 0, 0)

        self.btn_add = lv.btn(scr)
        self.btn_add.set_width(btn_width)
        self.btn_add.set_height(btn_width)
        self.btn_add.set_style_local_radius(lv.btn.PART.MAIN,lv.STATE.DEFAULT,btn_corner_radius)
        self.btn_add.align(None, lv.ALIGN.IN_TOP_RIGHT, 0,0)
        self.btn_add.set_event_cb(self.btn_add_cb)
        self.btn_add_label = lv.label(self.btn_add)
        self.btn_add_label.set_text("Add")

        self.btn_view = lv.btn(scr)
        self.btn_view.set_width(btn_width)
        self.btn_view.set_height(btn_width)
        self.btn_view.set_style_local_radius(lv.btn.PART.MAIN,lv.STATE.DEFAULT,btn_corner_radius)
        self.btn_view.align(None, lv.ALIGN.IN_TOP_RIGHT, 0,btn_width)
        self.btn_view.set_event_cb(self.btn_view_cb)
        self.btn_view_label = lv.label(self.btn_view)
        self.btn_view_label.set_text("View\nList")

        self.btn_clear = lv.btn(scr)
        self.btn_clear.set_width(btn_width)
        self.btn_clear.set_height(int(btn_width/2))
        self.btn_clear.set_style_local_radius(lv.btn.PART.MAIN,lv.STATE.DEFAULT,btn_corner_radius)
        self.btn_clear.align(None, lv.ALIGN.IN_BOTTOM_RIGHT, 0, -txt_height)
        self.btn_clear.set_event_cb(self.btn_clear_cb)
        self.btn_clear_label = lv.label(self.btn_clear)
        self.btn_clear_label.set_text("Clear")
        self.selected_product = ""

    def highlight_products_on_shopping_list(self):
        # Highlight items in the shopping list.
        for p in self.displayed:
            if p in self.shopping_list:
                self.displayed[p].set_style_local_bg_color(0, 0, lv.color_make(128,255,128))
            else:
                self.displayed[p].set_style_local_bg_color(0, 0, lv.color_make(255,255,255))

    def sync_displayed_products(self, products):
        to_remove_from_displayed = []
        for disp in self.displayed:
            if disp not in products:
                i = self.product_list.get_btn_index(self.displayed[disp])
                self.product_list.remove(i)
                to_remove_from_displayed.append(disp)
            else:
                products.remove(disp)
        for product in products:
            self.displayed[product] = self.product_list.add_btn(None, product)
            self.displayed[product].set_event_cb(self.product_list_cb)
        for disp in to_remove_from_displayed:
            self.displayed.pop(disp)
        self.highlight_products_on_shopping_list()

    def mainloop(self):
        print("Looping")
        self.keyboard.new = True
        products = []
        self.displayed = {}
        while True:
            kb_timeout = time.ticks_ms()
            flag = False
            idle_time_ms = 0
            while idle_time_ms < KB_ENTRY_COMMIT_TIMEOUT_MS or not flag:
                idle_time_ms = time.ticks_diff(time.ticks_ms(), kb_timeout)
                if manage_input_box(self.keyboard, self.buffer_text):
                    # If a button is pressed, restart the timer.
                    flag = True
                    kb_timeout = time.ticks_ms()
                if idle_time_ms > CHANGE_SYNC_MS and self.shopping_list_changed:
                    # If we are idle for a while, sync the shopping list with grocy.
                    self.g.sync()
                    self.g.set_shopping_list(self.shopping_list)
                    self.shopping_list_changed = False
                if idle_time_ms > IDLE_SYNC_MS:
                    # If we are idle for a long while, trigger a background sync.
                    self.g.sync()
            if self.mode == "browse":
                products = list(self.g.search_product_names_by_name(self.buffer_text.get_text()))
                self.sync_displayed_products(products)
            elif self.mode == "view":
                # This passes in a copy of the shopping list set
                self.sync_displayed_products(list(self.shopping_list))