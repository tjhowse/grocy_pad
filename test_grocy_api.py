#!/usr/bin/python3

from src.grocy_api import grocy_api
from src.secrets import *
g = grocy_api(grocy_api_key, grocy_domain)
g.sync()

for b in g.get_shopping_list():
    print(b)

g.add_product_to_shopping_list("Honey")

g.sync()

for b in g.get_shopping_list():
    print(b)