from __future__ import absolute_import, division, print_function, unicode_literals

from datetime import date
from dateutil.relativedelta import relativedelta
from decimal import Decimal
import random

from amaascore.assets.equity import Equity
from amaascore.assets.interface import AssetsInterface
from amaascore.books.book import Book
from amaascore.books.interface import BooksInterface
from amaascore.core.reference import Reference
from amaascore.parties.broker import Broker
from amaascore.parties.company import Company
from amaascore.parties.interface import PartiesInterface
from amaascore.transactions.interface import TransactionsInterface
from amaascore.transactions.transaction import Transaction

import logging
logging.basicConfig(level=logging.INFO)

# Create the interfaces
assets_interface = AssetsInterface()
books_interface = BooksInterface()
parties_interface = PartiesInterface()
transaction_interface = TransactionsInterface()


def create_assets(asset_manager_id):
    hsbc_symbol = '0005.HK'
    hsbc_references = {'ISIN': Reference(reference_value='GB0005405286'),
                       'Ticker': Reference(reference_value=hsbc_symbol)}

    hsbc = Equity(asset_manager_id=asset_manager_id,
                  asset_id=hsbc_symbol,
                  currency='HKD',
                  references=hsbc_references)

    assets_interface.new(hsbc)
    return hsbc


def create_parties(asset_manager_id, asset_manager_party_id, broker_id, base_currency):

    asset_manager = Company(asset_manager_id=asset_manager_id, party_id=asset_manager_party_id,
                            base_currency=base_currency)
    parties_interface.new(asset_manager)
    broker = Broker(asset_manager_id=asset_manager_id, party_id=broker_id)
    parties_interface.new(broker)


def create_books(asset_manager_id, asset_manager_party_id, trading_book_id, broker_id):
    trading_book = Book(asset_manager_id=asset_manager_id, book_id=trading_book_id, party_id=asset_manager_party_id)
    books_interface.new(trading_book)

    broker_book = Book(asset_manager_id=asset_manager_id, book_id=broker_id, party_id=broker_id)
    books_interface.new(broker_book)
    return trading_book, broker_book


def main():
    logging.info("--- SETTING UP IDENTIFIERS ---")
    asset_manager_id = random.randint(1, 2**31-1)
    asset_manager_party_id = 'AMID' + str(asset_manager_id)
    trading_book_id = 'DEMO-BOOK'
    broker_id = 'BROKER'
    currency = 'USD'
    today = date.today()
    settlement_date = today + relativedelta(days=2)

    # Create the books
    logging.info("--- SETTING UP BOOKS ---")
    trading_book, broker_book = create_books(asset_manager_id=asset_manager_id,
                                             asset_manager_party_id=asset_manager_party_id,
                                             trading_book_id=trading_book_id, broker_id=broker_id)

    # Create parties - obviously this normally would be a one-time setup thing
    logging.info("--- SETTING UP PARTIES ---")
    create_parties(asset_manager_id=asset_manager_id,
                   asset_manager_party_id=asset_manager_party_id,
                   broker_id=broker_id, base_currency=currency)

    # Create assets - things like HSBC would be centrally setup with AMID 0
    logging.info("--- SETTING UP ASSETS ---")
    hsbc = create_assets(asset_manager_id=asset_manager_id)

    # Trading Activity
    logging.info("--- BOOKING TRADES ---")
    logging.info("** BUY HSBC **")
    transaction1 = Transaction(asset_manager_id=asset_manager_id,
                               transaction_id='transaction1',
                               transaction_action='Buy',
                               asset_book_id=trading_book.book_id,
                               counterparty_book_id=broker_book.book_id,
                               asset_id=hsbc.asset_id,
                               transaction_currency=hsbc.currency,
                               transaction_date=today,
                               settlement_date=settlement_date,
                               quantity=Decimal('100'),
                               price=Decimal('63')
                               )
    transaction_interface.new(transaction1)
    logging.info("** SELL HSBC **")
    transaction2 = Transaction(asset_manager_id=asset_manager_id,
                               transaction_id='transaction2',
                               transaction_action='Sell',
                               asset_book_id=trading_book.book_id,
                               counterparty_book_id=broker_book.book_id,
                               asset_id=hsbc.asset_id,
                               transaction_currency=hsbc.currency,
                               transaction_date=today,
                               settlement_date=settlement_date,
                               quantity=Decimal('50'),
                               price=Decimal('63.5')
                               )
    transaction_interface.new(transaction2)
    logging.info("--- SHOW TRADING POSITIONS ---")
    positions = transaction_interface.position_search(asset_manager_ids=[asset_manager_id],
                                                      book_ids=[trading_book.book_id],
                                                      accounting_types=['Transaction Date'])
    for position in positions:
        logging.info(' | '.join([position.book_id, str(position.quantity), position.asset_id]))

if __name__ == '__main__':
    main()
