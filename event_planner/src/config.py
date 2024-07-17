import json
import os

JSON_PATH = os.path.join(os.path.dirname(__file__), 'item_options.json')
CONFIG_PATH = os.path.join(os.path.dirname(__file__), 'config.json')

def load_config():
    with open(CONFIG_PATH, 'r', encoding='utf-8') as file:
        return json.load(file)

def load_item_options():
    with open(JSON_PATH, 'r', encoding='utf-8') as file:
        return json.load(file)

config = load_config()
item_options = load_item_options()

EVENT_TYPES = item_options['EVENT_TYPES']
CONTRACT_TYPES = item_options['CONTRACT_TYPES']
STATUS_OPTIONS = item_options['STATUS_OPTIONS']
MEDIA_ITEMS = item_options['MEDIA_ITEMS']
CATEGORIES = item_options['CATEGORIES']
CATEGORY_ICONS = item_options['CATEGORY_ICONS']

CONTRACT_STATUS_OPTIONS = config['CONTRACT_STATUS_OPTIONS']
VAT_OPTIONS = config['VAT_OPTIONS']
SETUP_OPTIONS = config['SETUP_OPTIONS']
TEARDOWN_OPTIONS = config['TEARDOWN_OPTIONS']