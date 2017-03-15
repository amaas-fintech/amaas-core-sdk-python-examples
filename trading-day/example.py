from datetime import date
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

# Create the interfaces
assets_interface = AssetsInterface()
books_interface = BooksInterface()
parties_interface = PartiesInterface()
transaction_interface = TransactionsInterface()


def create_parties(asset_manager_id, fund_id, investor_id, base_currency):
    fund = Fund(asset_manager_id=asset_manager_id, party_id=fund_id, base_currency=base_currency)
    parties_interface.new(fund)
    investor = Individual(asset_manager_id=asset_manager_id, party_id=investor_id)
    parties_interface.new(investor)
    return fund, investor


def create_books(asset_manager_id, trading_book_id, broker_id):
    trading_book = Book(asset_manager_id=asset_manager_id, book_id=trading_book_id
    books_interface.new(trading_book)

    broker_book = Book(asset_manager_id=asset_manager_id, book_id=broker_id)
    books_interface.new(broker_book)

    return trading_book, broker_book


def main():
    asset_manager_id = random.randint(1, 2**32-1)
    trading_book_id = 'DEMO-BOOK'
    broker_id = 'BROKER'
    currency = 'USD'

    # Create the books
    trading_book, broker_book = create_books(asset_manager_id=asset_manager_id, trading_book_id=trading_book_id,
                                             broker_id=broker_id)

    # Create parties
    fund, investor = create_parties(asset_manager_id=asset_manager_id, fund_id=fund_id, investor_id=investor_id,
                                    base_currency=currency)

    asset = Equity(asset_manager_id=asset_manager_id,
                   asset_id=fund_id,
                   asset_issuer_id=fund_id,
                   currency=currency)

    assets_interface.new(asset)

    # Trading Activity
    # TRADES!!!

if __name__ == '__main__':
    main()
