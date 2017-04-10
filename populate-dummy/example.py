""" An example of how to setup a whole set of transactions for testing purposes. """
from __future__ import absolute_import, division, print_function, unicode_literals

from amaasutils.random_utils import random_string
from datetime import date
from decimal import Decimal
import logging
import logging.config
import random

from amaascore.assets.equity import Equity
from amaascore.assets.interface import AssetsInterface
from amaascore.books.book import Book
from amaascore.books.interface import BooksInterface
from amaascore.config import DEFAULT_LOGGING
from amaascore.core.reference import Reference
from amaascore.parties.broker import Broker
from amaascore.parties.company import Company
from amaascore.parties.individual import Individual
from amaascore.parties.interface import PartiesInterface
from amaascore.transactions.interface import TransactionsInterface
from amaascore.transactions.transaction import Transaction
from dateutil.relativedelta import relativedelta

logging.config.dictConfig(DEFAULT_LOGGING)

# Create the interfaces
assets_interface = AssetsInterface()
books_interface = BooksInterface()
parties_interface = PartiesInterface()
transaction_interface = TransactionsInterface()
currencies = ['HKD', 'SGD', 'USD']


def create_equity(asset_manager_id, asset_id):
    """ Create an equity for use in this example. """
    references = {'ISIN': Reference(reference_value=random_string(12)),
                  'Ticker': Reference(reference_value=random_string(8))}

    asset = Equity(asset_manager_id=asset_manager_id,
                   asset_id=asset_id,
                   currency=random.choice(currencies),
                   references=references)
    assets_interface.new(asset)
    return asset


def create_parties(asset_manager_id, asset_manager_party_id, broker_id, base_currency):
    """ Creates the parties used in this example: an asset manager and a broker. """
    asset_manager = Company(asset_manager_id=asset_manager_id, party_id=asset_manager_party_id,
                            base_currency=base_currency)
    parties_interface.new(asset_manager)
    broker = Broker(asset_manager_id=asset_manager_id, party_id=broker_id)
    parties_interface.new(broker)
    return asset_manager, broker


def create_book(asset_manager_id, book_id, party_id, owner_id=None):
    """ Creates a trading book for use in this example. """
    trading_book = Book(asset_manager_id=asset_manager_id, book_id=book_id, party_id=party_id, owner_id=owner_id)
    books_interface.new(trading_book)
    return trading_book


def create_transaction(asset_manager_id, transaction_id, asset_book_id, cpty_book_id, asset_id, transaction_date,
                       settlement_date):
    quantity = Decimal(random.randint(1, 1000))
    price = Decimal(random.random()).quantize(Decimal('0.01'))
    transaction = Transaction(asset_manager_id=asset_manager_id, transaction_id=transaction_id,
                              transaction_action=random.choice(['Buy', 'Sell']), asset_book_id=asset_book_id,
                              counterparty_book_id=cpty_book_id, asset_id=asset_id,
                              transaction_currency=random.choice(currencies),
                              transaction_date=transaction_date, settlement_date=settlement_date, quantity=quantity,
                              price=price)
    transaction_interface.new(transaction)


def main():
    """ Main example """
    logging.info("--- SETTING UP IDENTIFIERS ---")
    asset_manager_id = random.randint(1, 2**31-1)
    asset_manager_party_id = 'AMID' + str(asset_manager_id)
    traders = [('TJ', 'Joe', 'Trader'), ('GG', 'Gordon', 'Gekko'), ('AP', 'Patrick', 'Bateman')]
    brokers = [('BROKER1', 'Best Brokers Inc.'), ('BROKER2', 'World Broker')]
    no_of_books = 5
    no_of_equities = 10
    no_of_transactions = 100
    currency = 'USD'
    today = date.today()
    settlement_date = today + relativedelta(days=2)

    # Create the books
    logging.info("--- SETTING UP BOOKS ---")
    transaction_book_fields = ['asset_manager_id', 'book_id', 'party_id', 'book_status', 'description']
    book_ids = ['BOOK' + str(i+1) for i in range(no_of_books)]
    for book_id in book_ids:
        book = create_book(asset_manager_id=asset_manager_id, book_id=book_id, party_id=asset_manager_party_id,
                           owner_id=random.choice([trader[0] for trader in traders]))
        ### TEMP TEMP TEMP  ###
        book_json = book.to_json()
        trading_book_json = {attr: book_json.get(attr) for attr in transaction_book_fields}
        transaction_interface.upsert_transaction_book(transaction_book_json=trading_book_json)


    for broker in brokers:
        book = create_book(asset_manager_id=asset_manager_id, book_id=broker[0], party_id=broker[0])
        ### TEMP TEMP TEMP  ###
        book_json = book.to_json()
        trading_book_json = {attr: book_json.get(attr) for attr in transaction_book_fields}
        transaction_interface.upsert_transaction_book(transaction_book_json=trading_book_json)

    # Create parties
    logging.info("--- SETTING UP PARTIES ---")
    for trader_id, first_name, surname in traders:
        individual = Individual(asset_manager_id=asset_manager_id, party_id=trader_id, given_names=first_name,
                                surname=surname)
        parties_interface.new(individual)

    for broker_id, broker_name in brokers:
        broker = Broker(asset_manager_id=asset_manager_id, party_id=broker_id, description=broker_name)
        parties_interface.new(broker)

    # Create equities
    transaction_asset_fields = ['asset_manager_id', 'asset_id', 'asset_status', 'asset_class', 'asset_type', 'fungible']
    logging.info("--- SETTING UP EQUITIES ---")
    for i in range(no_of_equities):
        asset_id = 'EQ' + str(i+1)
        asset = create_equity(asset_manager_id=asset_manager_id, asset_id=asset_id)
        ### TEMP TEMP TEMP  ###
        asset_json = asset.to_json()
        transaction_asset_json = {attr: asset_json.get(attr) for attr in transaction_asset_fields}
        transaction_interface.upsert_transaction_asset(transaction_asset_json=transaction_asset_json)

    # Trading Activity
    logging.info("--- BOOKING TRADES ---")
    for i in range(no_of_transactions):
        transaction_id = str(i+1)
        asset_book_id = random.choice(book_ids)
        cpty_book_id = random.choice([broker[0] for broker in brokers])
        asset_id = 'EQ' + str(random.randint(1, no_of_equities))
        create_transaction(asset_manager_id=asset_manager_id, transaction_id=transaction_id, asset_id=asset_id,
                           asset_book_id=asset_book_id, cpty_book_id=cpty_book_id, transaction_date=today, 
                           settlement_date=settlement_date)

if __name__ == '__main__':
    main()
