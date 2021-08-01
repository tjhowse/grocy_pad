#!/usr/bin/python3
try:
    import urequests as requests
except ImportError:
    import requests
import json
# from datetime import datetime
import os
import time

class grocy_api:
    # Don't sync with the server inside this timeframe unless forced
    SYNC_RATE_MS = 120*1000

    def __init__(self, api_key, domain):
        self.base_url = '{}/api/'.format(domain)
        self.headers = {
                        'content-type': 'application/json',
                        'GROCY-API-KEY': api_key
                        }
        self.tables = {}
        self.entity_names = [   'products',
                                # 'recipes',
                                # 'quantity_units',
                                'shopping_list',
                                'stock',
                            ]
        self.db_changed_time = None
        self.last_sync_time = 0

    def get_db_changed(self):
        ### Returns True if the database has changed since last sync
        url = '{}system/db-changed-time'.format(self.base_url)
        response = requests.get(url, headers=self.headers)
        if response.status_code != 200:
            print(response.text)
        time = json.loads(response.text)
        if self.db_changed_time is None or self.db_changed_time != time['changed_time']:
            self.db_changed_time = time['changed_time']
            return True
        return False

    def sync_required(self):
        ### Returns true if it's been more than self.SYNC_RATE_MS since a sync.
        try:
            # This is micropython-specific.
            required = time.ticks_diff(time.ticks_ms(), self.last_sync_time) > self.SYNC_RATE_MS
        except AttributeError:
            required = True
        return required

    def sync(self, force=False):
        ### Syncs the database with the server
        if not self.sync_required() and not force:
            return
        try:
            self.last_sync_time = time.ticks_ms()
        except AttributeError:
            self.last_sync_time = 0
        if not self.get_db_changed():
            return
        for entity in self.entity_names:
            self.sync_entity(entity)

    def set_shopping_list(self, sl, skip_sync = False):
        ### Adds and removes products from the shopping list
        if not skip_sync:
            self.sync_entity("shopping_list")
        current = set(self.get_shopping_list())
        # Using sets like this minimises the number of calls to the API.
        for product in (sl - current):
            self.add_product_to_shopping_list(product)
        for product in (current - sl):
            self.remove_product_from_shopping_list(product)

    def set_stock_list(self, sl, skip_sync = False):
        ### Adds and removes products from the shopping list
        if not skip_sync:
            self.sync_entity("stock")
        current = set(self.get_stock_list())
        # Using sets like this minimises the number of calls to the API.
        for product in (sl - current):
            self.add_product_to_stock_list(product)
        for product in (current - sl):
            self.remove_product_from_stock_list(product)

    def sync_entity(self, entity_name):
        url = '{}objects/{}'.format(self.base_url, entity_name)
        response = requests.get(url, headers=self.headers)
        if response.status_code != 200:
            print(response.text)
        raw = json.loads(response.text)
        self.tables[entity_name] = {}
        for entity in raw:
            self.tables[entity_name][entity['id']] = entity

    def get_shopping_list(self):
        for id in self.tables['shopping_list']:
            product = self.tables['shopping_list'][id]
            name = self.tables['products'][product['product_id']]['name']
            yield name

    def get_stock_list(self):
        for id in self.tables['stock']:
            product = self.tables['stock'][id]
            name = self.tables['products'][product['product_id']]['name']
            yield name

    def get_recipe_list(self):
        ### Returns a list of recipies
        result = {}
        for id, recipe in self.tables['recipes'].items():
            if recipe['description'] is None:
                continue
            result[id] = recipe['name']
        return result

    def add_recipe_to_shopping_list(self, recipe_id):
        ### Adds a recipe to the shopping list
        url = '{}recipes/{}/add-not-fulfilled-products-to-shoppinglist'.format(self.base_url, recipe_id)
        response = requests.post(url, headers=self.headers)
        print(response)
        if response.status_code != 204:
            print(response.text)
        return response.text

    def search_product_names_by_name(self, name):
        ### Generates a list of product names.
        for id in self.tables['products']:
            product = self.tables['products'][id]
            if name.lower() in product['name'].lower():
                yield product['name']

    def search_stocked_product_names_by_name(self, name):
        ### Generates a list of product names.
        for stock_name in self.get_stock_list():
            if name.lower() in stock_name.lower():
                yield stock_name

    def get_product_id_with_name(self, product_name):
        ### Returns the product id of a product with the given name
        for id in self.tables['products']:
            product = self.tables['products'][id]
            if product['name'] == product_name:
                return product['id']
        return None

    def add_product_to_shopping_list(self, product):
        ### Adds a product to the shopping list by name
        url = '{}stock/shoppinglist/add-product'.format(self.base_url)
        add =   {
                    "product_id": self.get_product_id_with_name(product),
                    "list_id": 1,
                    "product_amount": 1,
                    "note": ""
                }
        response = requests.post(url, headers=self.headers, data=json.dumps(add))
        if response.status_code != 204:
            print(response.text)

    def remove_product_from_shopping_list(self, product):
        ### Removes a product to the shopping list by name
        url = '{}stock/shoppinglist/remove-product'.format(self.base_url)
        add =   {
                    "product_id": self.get_product_id_with_name(product),
                    "list_id": 1,
                    "product_amount": 1000,
                }
        response = requests.post(url, headers=self.headers, data=json.dumps(add))
        if response.status_code != 204:
            print(response.text)

    def add_product_to_stock(self, product):
        ### Adds a product to the stock list by name
        url = '{}stock/products/{}/add'.format(self.base_url, self.get_product_id_with_name(product))
        add =   {
                    "amount": 1
                }
        response = requests.post(url, headers=self.headers, data=json.dumps(add))
        if response.status_code != 200:
            print(response.text)

    def remove_product_from_stock(self, product):
        ### Removes a product from the stock list by name
        url = '{}stock/products/{}/inventory'.format(self.base_url, self.get_product_id_with_name(product))
        add =   {
                    "new_amount": 0
                }
        response = requests.post(url, headers=self.headers, data=json.dumps(add))
        if response.status_code != 200:
            print(response.text)

if __name__ == '__main__':
    key = os.getenv('GROCY_API_KEY')
    domain = "https://{}".format(os.getenv('GROCY_DOMAIN'))
    g = grocy_api(key, domain)
    g.sync()
    for product in g.search_products_by_name('sugar'):
        print(product['name'])