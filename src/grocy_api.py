#!/usr/bin/python3
try:
    import urequests as requests
except ImportError:
    import requests
import json
# from datetime import datetime
import os

class grocy_api:
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
                                # 'shopping_list',
                                # 'shopping_lists',
                            ]
        self.db_changed_time = None

    def get_db_changed_time(self):
        ### Returns the time of the last change in the database
        url = '{}system/db-changed-time'.format(self.base_url)
        response = requests.get(url, headers=self.headers)
        if response.status_code != 200:
            print(response.text)
        time = json.loads(response.text)
        return time['changed_time']

    def sync(self):
        ### Syncs the database with the server
        db_changed_time = self.get_db_changed_time()
        if self.db_changed_time is None or self.db_changed_time != db_changed_time:
            self.db_changed_time = db_changed_time
        else:
            # Nothing's change since last
            return
        for entity in self.entity_names:
            self.sync_entity(entity)

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
        ### Returns a string of the current shopping list
        result = []
        for id, product in self.tables['shopping_list'].items():
            amount = product['amount']
            unit = g.tables['quantity_units'][product['qu_id']]['name']
            name = g.tables['products'][product['product_id']]['name']
            print('{} {} {}'.format(amount, unit, name))

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
        result = []
        for id in self.tables['products']:
            product = self.tables['products'][id]
            if name.lower() in product['name'].lower():
                yield product['name']

if __name__ == '__main__':
    key = os.getenv('GROCY_API_KEY')
    domain = "https://{}".format(os.getenv('GROCY_DOMAIN'))
    g = grocy_api(key, domain)
    g.sync()
    for product in g.search_products_by_name('sugar'):
        print(product['name'])