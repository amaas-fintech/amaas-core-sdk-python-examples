""" An example of connecting to Yahoo Finance for market data. """
from __future__ import absolute_import, division, print_function, unicode_literals

from business_calendar import Calendar
from datetime import date
from decimal import Decimal
import logging
import logging.config
import random

from yahoo_finance import Share

from amaascore.assets.interface import AssetsInterface
from amaascore.config import DEFAULT_LOGGING
from amaascore.market_data.eod_price import EODPrice
from amaascore.market_data.interface import MarketDataInterface

logging.config.dictConfig(DEFAULT_LOGGING)

assets_interface = AssetsInterface()
market_data_interface = MarketDataInterface()


def main():
    """ Main example """
    logging.info("--- SETTING UP IDENTIFIERS ---")
    asset_manager_id = random.randint(1, 2**31-1)
    calendar = Calendar()
    # This can fail if yesterday was a holiday - need to add a holiday calendar
    business_date = calendar.addbusdays(date.today(), -2)
    logging.info("Business Date: %s", business_date)
    business_date_str = business_date.isoformat()
    symbols = ['TWTR', 'AAPL', 'RBS.L', 'Z77.SI', '0008.HK']

    logging.info("--- PULL MARKET DATA FROM YAHOO FINANCE ---")
    eod_prices = []
    for symbol in symbols:
        share = Share(symbol=symbol)
        logging.info("Stock Name: %s", share.get_name())
        close = (share.get_historical(start_date=business_date_str, end_date=business_date_str)[0].get('Close'))
        eod_price = EODPrice(asset_manager_id=asset_manager_id,
                             asset_id=symbol,
                             business_date=business_date,
                             price=Decimal(close))
        logging.info("EOD Price: %s", eod_price.price)
        eod_prices.append(eod_price)

    logging.info("--- PERSIST PRICES TO AMAAS ---")
    # Some of these attributes can be derived from the eod_prices - cleanup
    market_data_interface.persist_eod_prices(asset_manager_id=asset_manager_id, business_date=business_date,
                                             eod_prices=eod_prices, update_existing_prices=True)

if __name__ == '__main__':
    main()
