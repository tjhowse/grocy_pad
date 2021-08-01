from common import *

from page_shopping_list import page_shopping_list
from page_stock_list import page_stock_list

screen = M5Screen()
lv.scr_act().clean()
g = grocy_api(grocy_api_key, grocy_domain)

page_name = 'shopping_list'

while True:
    spinner = show_spinner()
    g.sync(force=True)
    spinner.delete()
    print("Starting page {}".format(page_name))
    if page_name == 'shopping_list':
        page = page_shopping_list(g)
        page_name = page.mainloop()
    elif page_name == 'stock_list':
        page = page_stock_list(g)
        page_name = page.mainloop()
