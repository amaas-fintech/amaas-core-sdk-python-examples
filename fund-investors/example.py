""" An example of setting up a fund with investors. """
from __future__ import absolute_import, division, print_function, unicode_literals

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
from amaascore.parties.fund import Fund
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


def create_parties(asset_manager_id, fund_id, trader_id, investor_id, base_currency):
    """ Create the parties used in this example: a fund, a trader and an investor. """
    fund = Fund(asset_manager_id=asset_manager_id, party_id=fund_id, base_currency=base_currency)
    parties_interface.new(fund)
    trader = Individual(asset_manager_id=asset_manager_id, party_id=trader_id)
    parties_interface.new(trader)
    investor = Individual(asset_manager_id=asset_manager_id, party_id=investor_id)
    parties_interface.new(investor)


def create_books(asset_manager_id, fund_id, trader_id, investor_id, issuance_id):
    """ Create the books used in this example: a fund book, an investor book and an issuance book. """
    fund_book = Book(asset_manager_id=asset_manager_id, book_id=fund_id, party_id=fund_id, owner_id=trader_id)
    books_interface.new(fund_book)

    investor_book = Book(asset_manager_id=asset_manager_id, book_id=investor_id, party_id=investor_id)
    books_interface.new(investor_book)

    issuance_book = Book(asset_manager_id=asset_manager_id, book_id=issuance_id, party_id=fund_id)
    books_interface.new(issuance_book)


def main():
    """ Main example """
    logging.info("--- SETTING UP IDENTIFIERS ---")
    asset_manager_id = random.randint(1, 2**31-1)
    fund_id = 'DEMO-FUND'
    trader_id = 'TRADER-JOE'
    investor_id = 'INVESTOR1'
    issuance_id = 'ISSUANCE'
    currency = 'USD'
    today = date.today()
    tomorrow = today + relativedelta(days=1)

    # Create parties
    logging.info("--- SETTING UP PARTIES ---")
    create_parties(asset_manager_id=asset_manager_id, fund_id=fund_id, trader_id=trader_id,
                   investor_id=investor_id, base_currency=currency)

    # Create the books
    logging.info("--- SETTING UP BOOKS ---")
    create_books(asset_manager_id=asset_manager_id, fund_id=fund_id, trader_id=trader_id,
                 investor_id=investor_id, issuance_id=issuance_id)

    logging.info("--- SETTING UP FUND EQUITY ---")
    asset = Equity(asset_manager_id=asset_manager_id,
                   asset_id=fund_id,
                   asset_issuer_id=fund_id,
                   currency=currency)
    assets_interface.new(asset)

    logging.info("--- ACQUIRE THE INITIAL FUND EQUITY TRANSACTION  ---")
    initial_transaction = Transaction(asset_manager_id=asset_manager_id,
                                      asset_book_id=fund_id,
                                      counterparty_book_id=issuance_id,
                                      transaction_id='SHARE-CREATION',
                                      transaction_action='Acquire',
                                      asset_id=fund_id,
                                      quantity=Decimal('100'),
                                      price=Decimal('0'),
                                      transaction_date=today,
                                      settlement_date=today,
                                      transaction_currency=currency,
                                      )
    transaction_interface.new(initial_transaction)

    logging.info("--- INVESTOR SUBSCRIBES ---")
    subscription = Transaction(asset_manager_id=asset_manager_id,
                               asset_book_id=fund_id,
                               counterparty_book_id=investor_id,
                               transaction_id='SUBSCRIPTION-ONE',
                               transaction_action='Subscription',
                               asset_id=fund_id,
                               quantity=Decimal('10'),
                               price=Decimal('1000000'),
                               transaction_date=today,
                               settlement_date=tomorrow,
                               transaction_currency=currency,
                               )
    transaction_interface.new(subscription)

    logging.info("--- SHOW HOLDINGS ---")
    positions = transaction_interface.position_search(asset_manager_ids=[asset_manager_id], asset_ids=[fund_id],
                                                      accounting_types=['Transaction Date'])
    for position in positions:
        logging.info(' | '.join([position.book_id, str(position.quantity), position.asset_id]))

if __name__ == '__main__':
    main()
