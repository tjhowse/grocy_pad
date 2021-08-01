from common import *

class page_stock_list:
    def btn_add_cb(self, obj, event):
        if event == lv.EVENT.CLICKED:
            self.input_ticks = time.ticks_ms()
            stocks_changed = False

            spinner = show_spinner()
            if self.btn_add_label.get_text() == "Mark\nBought":
                for disp in self.displayed:
                    if self.displayed[disp].get_style_bg_color(0).color_to32() == 4294934915:
                        # This is selected, remove it from the shopping list and add it to the stock list
                        print("Removing {} from shopping list and adding to stocks".format(disp))
                        self.shopping_list.remove(disp)
                        self.shopping_list_changed = True
                        self.g.add_product_to_stock(disp)
                        stocks_changed = True
            else:
                for disp in self.displayed:
                    if self.displayed[disp].get_style_bg_color(0).color_to32() == 4294934915:
                        # This is selected, remove it from the stock list
                        print("Removing {} from stocks".format(disp))
                        self.g.remove_product_from_stock(disp)
                        stocks_changed = True
            spinner.delete()
            if stocks_changed:
                spinner = show_spinner()
                self.g.sync()
                spinner.delete()
            self.reset_entry_state()

    def btn_view_cb(self, obj, event):
        if event == lv.EVENT.CLICKED:
            self.input_ticks = time.ticks_ms()
            if self.mode == "stocks":
                self.mode = "shopping_list"
                self.btn_add_label.set_text("Mark\nBought")
                self.btn_view_label.set_text("Stocks")
            else:
                self.mode = "stocks"
                self.btn_add_label.set_text("Mark\nUsed")
                self.btn_view_label.set_text("Shop\nList")
            self.reset_entry_state()

    def btn_clear_cb(self, obj, event):
        if event == lv.EVENT.CLICKED:
            self.input_ticks = time.ticks_ms()
            self.reset_entry_state()

    def product_list_cb(self, obj, event):
        if event == lv.EVENT.CLICKED:
            self.input_ticks = time.ticks_ms()
            list_btn = lv.list.__cast__(obj)
            colour = list_btn.get_style_bg_color(0).color_to32()
            print("Tapped colour {}".format(colour))
            # Note some of these colours don't correspond properly for reasons I haven't
            # worked out yet. I think maybe the "selected" state tints a row slightly?
            # lv.color_make(128,255,128).color_to32() == 4286840707
            # lv.color_make(255,128,128).color_to32() == 4294934915
            # lv.color_make(255,255,255).color_to32() == 4294967295
            if colour != 4294966015:
                # Else make it white
                list_btn.set_style_local_bg_color(0, 0, lv.color_make(255,255,255))
            else:
                # If it was white, set it to red.
                list_btn.set_style_local_bg_color(0, 0, lv.color_make(255,128,128))

    def reset_entry_state(self):
        self.buffer_text.set_text("")
        self.keyboard.clear_buffer()
        self.keyboard.new = True
        for disp in self.displayed:
            self.displayed[disp].set_style_local_bg_color(0, 0, lv.color_make(255,255,255))

    def __init__(self, grocy):
        self.g = grocy
        scr = lv.scr_act()
        scr.clean()
        scr.set_style_local_bg_color(0, 0, lv.color_make(255,0,0))

        self.shopping_list = set(self.g.get_shopping_list())
        self.keyboard = i2c_kb(interrupt=None)
        self.mode = "stocks"
        self.shopping_list_changed = False
        # This stores the time of the last key or button press.
        self.input_ticks = 0

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
        self.btn_add_label.set_text("Mark\nUsed")

        self.btn_view = lv.btn(scr)
        self.btn_view.set_width(btn_width)
        self.btn_view.set_height(btn_width)
        self.btn_view.set_style_local_radius(lv.btn.PART.MAIN,lv.STATE.DEFAULT,btn_corner_radius)
        self.btn_view.align(None, lv.ALIGN.IN_TOP_RIGHT, 0,btn_width)
        self.btn_view.set_event_cb(self.btn_view_cb)
        self.btn_view_label = lv.label(self.btn_view)
        self.btn_view_label.set_text("Shop\nList")

        self.btn_clear = lv.btn(scr)
        self.btn_clear.set_width(btn_width)
        self.btn_clear.set_height(int(btn_width/2))
        self.btn_clear.set_style_local_radius(lv.btn.PART.MAIN,lv.STATE.DEFAULT,btn_corner_radius)
        self.btn_clear.align(None, lv.ALIGN.IN_BOTTOM_RIGHT, 0, -txt_height)
        self.btn_clear.set_event_cb(self.btn_clear_cb)
        self.btn_clear_label = lv.label(self.btn_clear)
        self.btn_clear_label.set_text("Clear")

        # 255 is the wifi symbol on the M5 FACES QWERTY keyboard. sym+$
        self.keyboard.register_char_callback(255, self.force_grocy_sync)
        btnA.wasPressed(self.buttonA_wasPressed)

    def buttonA_wasPressed(self):
        self.return_code = 'shopping_list'
        self.running = False
        print("Button A pressed, launching page {}".format(self.return_code))

    def force_grocy_sync(self):
        spinner = show_spinner()
        self.g.sync(force=True)
        spinner.delete()

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

    def mainloop(self):
        print("Looping")
        self.keyboard.new = True
        products = []
        self.displayed = {}
        self.running = True
        while self.running:
            self.input_ticks = time.ticks_ms()
            flag = False
            idle_time_ms = 0
            while (time.ticks_diff(time.ticks_ms(), self.input_ticks) < KB_ENTRY_COMMIT_TIMEOUT_MS or not flag) and self.running:
                if manage_input_box(self.keyboard, self.buffer_text):
                    # If a button is pressed, restart the timer.
                    flag = True
                    self.input_ticks = time.ticks_ms()
                idle_time_ms = time.ticks_diff(time.ticks_ms(), self.input_ticks)
                if idle_time_ms > CHANGE_SYNC_MS and self.shopping_list_changed:
                    # If we are idle for a while, sync the shopping list with grocy.
                    spinner = show_spinner()
                    self.g.sync()
                    self.g.set_shopping_list(self.shopping_list)
                    self.shopping_list_changed = False
                    spinner.delete()
                if idle_time_ms > IDLE_SYNC_MS and self.g.sync_required():
                    # If we are idle for a long while, trigger a background sync.
                    spinner = show_spinner()
                    self.g.sync()
                    self.shopping_list = set(self.g.get_shopping_list())
                    spinner.delete()
            if self.mode == "stocks":
                products = list(self.g.search_stocked_product_names_by_name(self.buffer_text.get_text()))
                self.sync_displayed_products(products)
            elif self.mode == "shopping_list":
                # This passes in a copy of the shopping list set
                self.sync_displayed_products(list(self.shopping_list))
        lv.scr_act().clean()
        return self.return_code