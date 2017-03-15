from __future__ import absolute_import, division, print_function, unicode_literals

from datetime import date
from dateutil.relativedelta import relativedelta
from decimal import Decimal
import random

from amaascore.assets.equity import Equity
from amaascore.assets.interface import AssetsInterface
from amaascore.books.book import Book
from amaascore.books.interface import BooksInterface
from amaascore.parties.fund import Fund
from amaascore.parties.individual import Individual
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


def create_parties(asset_manager_id, fund_id, trader_id, investor_id, base_currency):
    fund = Fund(asset_manager_id=asset_manager_id, party_id=fund_id, base_currency=base_currency)
    parties_interface.new(fund)
    trader = Individual(asset_manager_id=asset_manager_id, party_id=trader_id)
    parties_interface.new(trader)
    investor = Individual(asset_manager_id=asset_manager_id, party_id=investor_id)
    parties_interface.new(investor)
    return fund, investor, trader


def create_books(asset_manager_id, fund_id, trader_id, investor_id, issuance_id):
    fund_book = Book(asset_manager_id=asset_manager_id, book_id=fund_id, party_id=fund_id, owner_id=trader_id)
    books_interface.new(fund_book)

    investor_book = Book(asset_manager_id=asset_manager_id, book_id=investor_id, party_id=investor_id)
    books_interface.new(investor_book)

    issuance_book = Book(asset_manager_id=asset_manager_id, book_id=issuance_id, party_id=fund_id)
    books_interface.new(issuance_book)

    return fund_book, investor_book, issuance_book


def main():
    logging.info("--- SETTING UP IDENTIFIERS ---")
    asset_manager_id = random.randint(1, 2**32-1)
    fund_id = 'DEMO-FUND'
    trader_id = 'TRADER-JOE'
    investor_id = 'INVESTOR1'
    issuance_id = 'ISSUANCE'
    currency = 'USD'
    today = date.today()
    tomorrow = today + relativedelta(days=1)

    # Create parties
    logging.info("--- SETTING UP PARTIES ---")
    fund, trader, investor = create_parties(asset_manager_id=asset_manager_id, fund_id=fund_id, trader_id=trader_id,
                                            investor_id=investor_id, base_currency=currency)

    # Create the books
    logging.info("--- SETTING UP BOOKS ---")
    fund_book, investor_book, issuance_book = create_books(asset_manager_id=asset_manager_id, fund_id=fund_id,
                                                           trader_id=trader_id, investor_id=investor_id,
                                                           issuance_id=issuance_id)
    logging.info("--- SETTING UP FUND EQUITY ---")
    asset = Equity(asset_manager_id=asset_manager_id,
                   asset_id=fund_id,
                   asset_issuer_id=fund_id,
                   currency=currency)
    assets_interface.new(asset)


    # TEMP TEMP TEMP TEMP TEMP TEMP TEMP TEMP
    transaction_asset_fields = ['asset_manager_id', 'asset_id', 'asset_status', 'asset_class', 'asset_type', 'fungible']
    asset_json = asset.to_json()
    transaction_asset_json = {attr: asset_json.get(attr) for attr in transaction_asset_fields}
    transaction_interface.upsert_transaction_asset(transaction_asset_json=transaction_asset_json)
    transaction_book_fields = ['asset_manager_id', 'book_id', 'party_id', 'book_status', 'description']
    fund_json = fund_book.to_json()
    fund_book_json = {attr: fund_json.get(attr) for attr in transaction_book_fields}
    transaction_interface.upsert_transaction_book(transaction_book_json=fund_book_json)
    issuance_json = issuance_book.to_json()
    issuance_book_json = {attr: issuance_json.get(attr) for attr in transaction_book_fields}
    transaction_interface.upsert_transaction_book(transaction_book_json=issuance_book_json)
    investor_json = investor_book.to_json()
    investor_book_json = {attr: investor_json.get(attr) for attr in transaction_book_fields}
    transaction_interface.upsert_transaction_book(transaction_book_json=investor_book_json)
    # ENDTEMP ENDTEMP ENDTEMP ENDTEMP ENDTEMP ENDTEMP

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
