from __future__ import absolute_import, division, print_function, unicode_literals

from datetime import date
from dateutil.relativedelta import relativedelta
from decimal import Decimal
import logging.config
import random

from amaascore.config import DEFAULT_LOGGING
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

logging.config.dictConfig(DEFAULT_LOGGING)

# Create the interfaces
assets_interface = AssetsInterface()
books_interface = BooksInterface()
parties_interface = PartiesInterface()
transaction_interface = TransactionsInterface()


def create_assets(asset_manager_id):
    singtel_symbol = 'Z77.SI'
    singtel_references = {'ISIN': Reference(reference_value='SG1T75931496'),
                          'Ticker': Reference(reference_value=singtel_symbol)}

    singtel = Equity(asset_manager_id=asset_manager_id, asset_id=singtel_symbol,
                     currency='SGD', references=singtel_references)

    assets_interface.new(singtel)
    return singtel


def create_parties(asset_manager_id, asset_manager_party_id, broker_id, base_currency):

    asset_manager = Company(asset_manager_id=asset_manager_id, party_id=asset_manager_party_id,
                            base_currency=base_currency)
    parties_interface.new(asset_manager)
    broker = Broker(asset_manager_id=asset_manager_id, party_id=broker_id)
    parties_interface.new(broker)
    return asset_manager, broker


def create_books(asset_manager_id, asset_manager_party_id, trading_book_id, broker_id):
    trading_book = Book(asset_manager_id=asset_manager_id, book_id=trading_book_id, party_id=asset_manager_party_id)
    books_interface.new(trading_book)

    broker_book = Book(asset_manager_id=asset_manager_id, book_id=broker_id, party_id=broker_id,
                       book_type='Counterparty')
    books_interface.new(broker_book)

    return trading_book, broker_book


def book_transaction(asset_manager_id, asset_book_id, counterparty_book_id, asset, transaction_date, settlement_date,
                     quantity):
    price = Decimal('3.92')  # Price of Singtel today :-)
    transaction = Transaction(asset_manager_id=asset_manager_id,
                              transaction_action='Buy',
                              asset_book_id=asset_book_id,
                              counterparty_book_id=counterparty_book_id,
                              asset_id=asset.asset_id,
                              transaction_currency=asset.currency,
                              transaction_date=transaction_date,
                              settlement_date=settlement_date,
                              quantity=quantity,
                              price=price)
    transaction = transaction_interface.new(transaction)
    return transaction.transaction_id


def main():
    logging.info("--- SETTING UP IDENTIFIERS ---")
    asset_manager_id = random.randint(1, 2**31-1)
    asset_manager_party_id = 'AMID' + str(asset_manager_id)
    trading_book_id = 'DEMO-BOOK'
    broker_id = 'BROKER'
    currency = 'USD'
    today = date.today()
    tomorrow = today + relativedelta(days=1)
    overmorrow = today + relativedelta(days=2)
    yesterday = today - relativedelta(days=1)
    ereyesterday = today - relativedelta(days=2)

    # Create the books
    logging.info("--- SETTING UP BOOKS ---")
    trading_book, broker_book = create_books(asset_manager_id=asset_manager_id,
                                             asset_manager_party_id=asset_manager_party_id,
                                             trading_book_id=trading_book_id, broker_id=broker_id)

    # Create parties - obviously this normally would be a one-time setup thing
    logging.info("--- SETTING UP PARTIES ---")
    asset_manager, broker = create_parties(asset_manager_id=asset_manager_id,
                                           asset_manager_party_id=asset_manager_party_id,
                                           broker_id=broker_id, base_currency=currency)

    # Create assets - things like Singtel would be centrally setup with AMID 0
    logging.info("--- SETTING UP ASSETS ---")
    singtel = create_assets(asset_manager_id=asset_manager_id)


    # Trading Activity
    logging.info("--- BOOKING TRADES ---")
    logging.info("** BUY SINGTEL **")
    book_transaction(asset_manager_id=asset_manager_id, asset_book_id=trading_book.book_id,
                     counterparty_book_id=broker_book.book_id, asset=singtel,
                     transaction_date=today, settlement_date=overmorrow,
                     quantity=Decimal('100'))

    logging.info("--- CURRENT POSITIONS AFTER FIRST TRADE ---")
    positions = transaction_interface.positions_by_asset_manager(asset_manager_id=asset_manager_id)
    for position in positions:
        logging.info(' | '.join([position.book_id, str(position.quantity), position.asset_id]))

    logging.info("--- BOOKING A TRADE FROM YESTERDAY ---")
    t_id2 = book_transaction(asset_manager_id=asset_manager_id, asset_book_id=trading_book.book_id,
                             counterparty_book_id=broker_book.book_id, asset=singtel,
                             transaction_date=yesterday, settlement_date=tomorrow,
                             quantity=Decimal('150'))

    logging.info("--- CURRENT POSITIONS AFTER SECOND TRADE ---")
    positions = transaction_interface.positions_by_asset_manager(asset_manager_id=asset_manager_id)
    for position in positions:
        logging.info(' | '.join([position.book_id, str(position.quantity), position.asset_id]))

    logging.info("--- BOOKING A TRADE FROM EREYESTERDAY ---")
    t_id3 = book_transaction(asset_manager_id=asset_manager_id, asset_book_id=trading_book.book_id,
                             counterparty_book_id=broker_book.book_id, asset=singtel,
                             transaction_date=ereyesterday, settlement_date=today,
                             quantity=Decimal('50'))

    logging.info("--- CURRENT POSITIONS AFTER THIRD TRADE ---")
    positions = transaction_interface.positions_by_asset_manager(asset_manager_id=asset_manager_id)
    for position in positions:
        logging.info(' | '.join([position.book_id, str(position.quantity), position.asset_id]))

    logging.info("--- YESTERDAY'S POSITIONS AFTER THIRD TRADE ---")
    positions = transaction_interface.position_search(asset_manager_ids=[asset_manager_id],
                                                      book_ids=[trading_book.book_id],
                                                      accounting_types=['Transaction Date'],
                                                      position_date=yesterday)
    for position in positions:
        logging.info(' | '.join([position.book_id, str(position.quantity), position.asset_id]))

    logging.info("--- CANCEL YESTERDAY'S TRADE ---")
    transaction_interface.cancel(asset_manager_id=asset_manager_id, transaction_id=t_id2)

    logging.info("--- CURRENT POSITIONS AFTER CANCELLATION ---")
    positions = transaction_interface.positions_by_asset_manager(asset_manager_id=asset_manager_id)
    for position in positions:
        logging.info(' | '.join([position.book_id, str(position.quantity), position.asset_id]))

    logging.info("--- YESTERDAY'S POSITIONS AFTER CANCELLATION ---")
    positions = transaction_interface.position_search(asset_manager_ids=[asset_manager_id],
                                                      book_ids=[trading_book.book_id],
                                                      accounting_types=['Transaction Date'],
                                                      position_date=yesterday)
    for position in positions:
        logging.info(' | '.join([position.book_id, str(position.quantity), position.asset_id]))

    logging.info("--- AMEND EREYESTERDAY'S TRADE ---")
    transaction = transaction_interface.retrieve(asset_manager_id=asset_manager_id, transaction_id=t_id3)
    transaction.quantity = 10
    transaction_interface.amend(transaction)

    logging.info("--- CURRENT POSITIONS AFTER AMEND ---")
    positions = transaction_interface.positions_by_asset_manager(asset_manager_id=asset_manager_id)
    for position in positions:
        logging.info(' | '.join([position.book_id, str(position.quantity), position.asset_id]))

    logging.info("--- YESTERDAY'S POSITIONS AFTER AMEND ---")
    positions = transaction_interface.position_search(asset_manager_ids=[asset_manager_id],
                                                      book_ids=[trading_book.book_id],
                                                      accounting_types=['Transaction Date'],
                                                      position_date=yesterday)
    for position in positions:
        logging.info(' | '.join([position.book_id, str(position.quantity), position.asset_id]))

if __name__ == '__main__':
    main()
