from common import *

from page_shopping_list import page_shopping_list
from page_stock_list import page_stock_list

screen = M5Screen()
lv.scr_act().clean()
msg = show_msg("Syncing with Grocy...", 10, 10)
spinner = show_spinner()
g = grocy_api(grocy_api_key, grocy_domain)
g.sync(force=True)
spinner.delete()
msg.delete()
show_msg("Sync done")

sl = page_shopping_list(g)
# sl = page_stock_list(g)
sl.mainloop()