from __future__ import absolute_import, division, print_function, unicode_literals

from datetime import date
from dateutil.relativedelta import relativedelta
from decimal import Decimal
import logging.config
import random

from amaascore.config import DEFAULT_LOGGING
from amaascore.assets.bond import BondGovernment
from amaascore.assets.interface import AssetsInterface
from amaascore.books.book import Book
from amaascore.books.interface import BooksInterface
from amaascore.core.reference import Reference
from amaascore.parties.broker import Broker
from amaascore.parties.company import Company
from amaascore.parties.interface import PartiesInterface
from amaascore.transactions.interface import TransactionsInterface
from amaascore.transactions.transaction import Transaction

logging.config.dictConfig(DEFAULT_LOGGING)

# Create the interfaces
assets_interface = AssetsInterface()
books_interface = BooksInterface()
parties_interface = PartiesInterface()
transaction_interface = TransactionsInterface()


def create_jgb(asset_manager_id):
    jgb_symbol = 'JB355'
    jgb_references = {'ISIN': Reference(reference_value='JP1234567890'),
                      'Ticker': Reference(reference_value=jgb_symbol)}

    jgb = BondGovernment(asset_manager_id=asset_manager_id, asset_id=jgb_symbol,
                         currency='JPY', references=jgb_references, coupon=Decimal('0.1'),
                         par=Decimal(50000), pay_frequency='Semi')

    assets_interface.new(jgb)
    return jgb


def create_books(asset_manager_id, asset_manager_party_id, book_one_id, book_two_id, wash_book_id, broker_id,
                 broker_book_id):
    book_one = Book(asset_manager_id=asset_manager_id, book_id=book_one_id, party_id=asset_manager_party_id)
    books_interface.new(book_one)
    book_two = Book(asset_manager_id=asset_manager_id, book_id=book_two_id, party_id=asset_manager_party_id)
    books_interface.new(book_two)
    wash_book = Book(asset_manager_id=asset_manager_id, book_id=wash_book_id, party_id=asset_manager_party_id,
                     book_type='Wash')
    books_interface.new(wash_book)
    broker_book = Book(asset_manager_id=asset_manager_id, book_id=broker_book_id, party_id=broker_id,
                       book_type='Counterparty')
    books_interface.new(broker_book)

    return book_one, book_two, wash_book, broker_book


def main():
    logging.info("--- SETTING UP IDENTIFIERS ---")
    asset_manager_id = random.randint(1, 2**31-1)
    asset_manager_party_id = 'AMID' + str(asset_manager_id)
    book_one_id = 'BOOK1'
    book_two_id = 'BOOK2'
    wash_book_id = 'WASH'
    broker_id = broker_book_id = 'BROKER'
    currency = 'JPY'

    # Create the books
    logging.info("--- SETTING UP BOOKS ---")
    book_one, book_two, wash_book, broker_book = create_books(asset_manager_id=asset_manager_id,
                                                              asset_manager_party_id=asset_manager_party_id,
                                                              book_one_id=book_one_id,
                                                              book_two_id=book_two_id,
                                                              wash_book_id=wash_book_id,
                                                              broker_id=broker_id,
                                                              broker_book_id=broker_book_id)

    # Create parties - obviously this normally would be a one-time setup thing
    logging.info("--- SETTING UP PARTIES ---")
    asset_manager = Company(asset_manager_id=asset_manager_id, party_id=asset_manager_party_id,
                            base_currency=currency)
    parties_interface.new(asset_manager)
    broker = Broker(asset_manager_id=asset_manager_id, party_id=broker_id, base_currency=currency)
    parties_interface.new(broker)

    # Create assets - things like a JGB would be centrally setup with AMID 0
    logging.info("--- SETTING UP ASSETS ---")
    jgb = create_jgb(asset_manager_id=asset_manager_id)

    # Trading Activity
    logging.info("--- BOOKING TRADES ---")
    logging.info("** BUY JGB **")
    transaction = Transaction(asset_manager_id=asset_manager_id,
                              transaction_action='Buy',
                              asset_book_id=book_one_id,
                              counterparty_book_id=broker_book_id,
                              asset_id=jgb.asset_id,
                              transaction_currency=jgb.currency,
                              transaction_date=date.today(),
                              settlement_date=date.today() + relativedelta(days=2),
                              quantity=1e06,
                              price=Decimal('100.487'))
    transaction_interface.new(transaction)

    logging.info("--- POSITIONS AFTER FIRST TRADE ---")
    positions = transaction_interface.positions_by_asset_manager(asset_manager_id=asset_manager_id)
    for position in positions:
        logging.info(' | '.join([position.book_id, str(position.quantity), position.asset_id]))

    logging.info("--- DO A BOOK TRANSFER ---")
    transaction_interface.book_transfer(asset_manager_id=asset_manager_id,
                                        source_book_id=book_one_id,
                                        target_book_id=book_two_id,
                                        wash_book_id=wash_book_id,
                                        asset_id=jgb.asset_id,
                                        quantity=500000,
                                        price=Decimal('100.45'),
                                        currency='JPY')

    logging.info("--- POSITIONS AFTER BOOK TRANSFER ---")
    positions = transaction_interface.positions_by_asset_manager(asset_manager_id=asset_manager_id)
    for position in positions:
        logging.info(' | '.join([position.book_id, str(position.quantity), position.asset_id]))

if __name__ == '__main__':
    main()
