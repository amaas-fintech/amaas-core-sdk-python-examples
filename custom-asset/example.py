from __future__ import absolute_import, division, print_function, unicode_literals

from amaascore.assets.asset import Asset
from amaascore.assets.interface import AssetsInterface
from amaascore.config import DEFAULT_LOGGING
import json
import logging.config
import random

logging.config.dictConfig(DEFAULT_LOGGING)


class Pizza(Asset):

    def __init__(self, size, asset_id, asset_manager_id, toppings=None, *args, **kwargs):
        self.size = size
        self.toppings = toppings
        client_additional = json.dumps({'size': self.size, 'toppings': self.toppings})
        super(Pizza, self).__init__(asset_manager_id=asset_manager_id, asset_id=asset_id,
                                    client_additional=client_additional, fungible=False)


def main():
    logging.info("--- SETTING UP ---")
    asset_manager_id = random.randint(1, 2**31-1)
    assets_interface = AssetsInterface()

    logging.info("--- CREATING PIZZA ---")
    pizza = Pizza(asset_id='pizza1', asset_manager_id=asset_manager_id,
                  size='Large', toppings=['pineapple', 'corn', 'garlic'])
    logging.info("--- SENDING PIZZA TO AMAAS ---")
    pizza = assets_interface.new(pizza)
    logging.info("RETURNED PIZZA TYPE IS: %s", type(pizza).__name__)
    logging.info("--- CASTING CUSTOM_TYPE BACK TO PIZZA ---")
    asset_attrs = pizza.to_dict()
    client_additional = json.loads(pizza.client_additional)
    size = client_additional.get('size')
    toppings = client_additional.get('toppings')
    pizza = Pizza(size=size, toppings=toppings, **asset_attrs)
    logging.info("PIZZA TYPE IS: %s", type(pizza).__name__)
    logging.info("PIZZA TOPPINGS ARE: %s", ', '.join(pizza.toppings))

if __name__ == '__main__':
    main()
