""" An example of how to load AMaaS Core Objects from CSV files. """
from __future__ import absolute_import, division, print_function, unicode_literals

from amaasutils.random_utils import random_string
from decimal import Decimal
import logging
import logging.config
import os
import random
import tempfile

from amaascore.assets.equity import Equity
from amaascore.assets.interface import AssetsInterface
from amaascore.assets.utils import json_to_asset
from amaascore.books.book import Book
from amaascore.books.interface import BooksInterface
from amaascore.books.utils import json_to_book
from amaascore.config import DEFAULT_LOGGING
from amaascore.core.reference import Reference
from amaascore.parties.broker import Broker
from amaascore.parties.individual import Individual
from amaascore.parties.interface import PartiesInterface
from amaascore.parties.party import Party
from amaascore.parties.utils import json_to_party
from amaascore.tools.csv_tools import csv_filename_to_objects, objects_to_csv
from amaascore.tools.generate_transaction import generate_transaction
from amaascore.transactions.interface import TransactionsInterface
from amaascore.transactions.transaction import Transaction
from amaascore.transactions.utils import json_to_transaction

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
    return asset


def create_book(asset_manager_id, book_id, party_id, owner_id=None):
    """ Creates a trading book for use in this example. """
    trading_book = Book(asset_manager_id=asset_manager_id, book_id=book_id, party_id=party_id, owner_id=owner_id)
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
                              price=price
                              )
    transaction_interface.new(transaction)


def main():
    """ Main example """
    logging.info("--- SETTING UP IDENTIFIERS ---")
    asset_manager_id = random.randint(1, 2**31-1)
    asset_manager_party_id = 'AMID' + str(asset_manager_id)
    traders = [('TJ', 'Joe', 'Trader'), ('GG', 'Gordon', 'Gekko'), ('AP', 'Patrick', 'Bateman')]
    brokers = [('BROKER1', 'Best Brokers Inc.'), ('BROKER2', 'World Broker')]
    csv_path = tempfile.gettempdir()  # Modify this to read and write from a different directory
    no_of_books = 5
    no_of_equities = 10
    no_of_transactions = 20

    logging.info("--- CREATING BOOKS CSV FILE ---")
    books = []
    asset_book_ids = ['BOOK' + str(i+1) for i in range(no_of_books)]
    for book_id in asset_book_ids:
        book = create_book(asset_manager_id=asset_manager_id, book_id=book_id, party_id=asset_manager_party_id,
                           owner_id=random.choice([trader[0] for trader in traders]))
        books.append(book)
    for broker in brokers:
        book = create_book(asset_manager_id=asset_manager_id, book_id=broker[0], party_id=broker[0])
        books.append(book)
    books_filename = os.path.join(csv_path, 'books.csv')
    logging.info("--- WRITING TO %s ---", books_filename)
    objects_to_csv(objects=books, clazz=Book, filename=books_filename)

    logging.info("--- CREATING PARTIES CSV FILE ---")
    parties = []
    for trader_id, first_name, surname in traders:
        individual = Individual(asset_manager_id=asset_manager_id, party_id=trader_id, given_names=first_name,
                                surname=surname)
        parties.append(individual)
    for broker_id, broker_name in brokers:
        broker = Broker(asset_manager_id=asset_manager_id, party_id=broker_id, description=broker_name)
        parties.append(broker)
    parties_filename = os.path.join(csv_path, 'parties.csv')
    logging.info("--- WRITING TO %s ---", parties_filename)
    objects_to_csv(objects=parties, clazz=Party, filename=parties_filename)

    logging.info("--- CREATING EQUITIES CSV FILE ---")
    assets = []
    asset_ids = ['EQ' + str(i+1) for i in range(no_of_equities)]
    for asset_id in asset_ids:
        asset = create_equity(asset_manager_id=asset_manager_id, asset_id=asset_id)
        assets.append(asset)
    equities_filename = os.path.join(csv_path, 'equities.csv')
    logging.info("--- WRITING TO %s ---", equities_filename)
    objects_to_csv(objects=assets, clazz=Equity, filename=equities_filename)

    logging.info("--- CREATING TRANSACTIONS CSV FILE ---")
    transactions = []
    for i in range(no_of_transactions):
        transaction_id = str(i+1)
        asset_id = random.choice(asset_ids)
        asset_book_id = random.choice(asset_book_ids)
        cpty_book_id = random.choice(['BROKER1', 'BROKER2'])
        transaction = generate_transaction(asset_manager_id=asset_manager_id, transaction_id=transaction_id,
                                           asset_id=asset_id,
                                           asset_book_id=asset_book_id, counterparty_book_id=cpty_book_id)
        transactions.append(transaction)
    transactions_filename = os.path.join(csv_path, 'transactions.csv')
    logging.info("--- WRITING TO %s ---", transactions_filename)
    objects_to_csv(objects=transactions, clazz=Transaction, filename=transactions_filename)

    logging.info("--- READING BOOKS CSV AND CREATING ---")
    books = csv_filename_to_objects(filename=books_filename, json_handler=json_to_book)
    for book in books:
        books_interface.new(book)

    logging.info("--- READING PARTIES CSV AND CREATING ---")
    parties = csv_filename_to_objects(filename=parties_filename, json_handler=json_to_party)
    for party in parties:
        parties_interface.new(party)

    logging.info("--- READING EQUITIES CSV AND CREATING ---")
    equities = csv_filename_to_objects(filename=equities_filename, json_handler=json_to_asset)
    for equity in equities:
        assets_interface.new(equity)

    logging.info("--- READING TRANSACTIONS CSV AND CREATING ---")
    transactions = csv_filename_to_objects(filename=transactions_filename, json_handler=json_to_transaction)
    for transaction in transactions:
        transaction_interface.new(transaction)

if __name__ == '__main__':
    main()
