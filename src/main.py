import argparse
import logging

import src.utils.sql_actions as dba # pragma: no cover

from src.aliexpress import aliexpress
from src.craigslist import craigslist
from src.ebay import search

logging.basicConfig(level='INFO')
logger = logging.getLogger(__name__)


class GetProducts():

    def __init__(self, args_dict):
        self.aliexpress = aliexpress.run(args_dict)
        self.craigslist = craigslist.run(args_dict)
        self.ebay = search.run(args_dict)

    def __repr__(self):
        return f"GetProducts(" \
               f"AliExpress: {self.aliexpress}\n" \
               f"Craigslist: {self.craigslist}\n " \
               f"Ebay: {self.ebay}"


def run_all(args_dict): # pragma: no cover
    data = GetProducts(args_dict)

    ebay_records = [dba.SearchResult(
            name=d['productName'],
            url=d['listingUrl'],
            price=d['salePrice'],
            query=args_dict['query'],
            website_id=1,
        ) for d in data.ebay[0] if not isinstance(d['salePrice'], tuple)]
    dba.session.add_all(ebay_records)

    aliexpress_records = [dba.SearchResult(
            name=d['productName'],
            url=d['listingUrl'],
            price=d['salePrice'],
            query=args_dict['query'],
            website_id=3,
        ) for d in data.aliexpress if not isinstance(d['salePrice'], tuple)]
    dba.session.add_all(aliexpress_records)

    craigslist_records = [dba.SearchResult(
            name=d['productName'],
            url=d['listingUrl'],
            price=d['salePrice'],
            query=args_dict['query'],
            website_id=2,
        ) for d in data.craigslist if not isinstance(d['salePrice'], tuple)]
    dba.session.add_all(craigslist_records)

    dba.session.commit()

    return str(data.__repr__())


if __name__ == '__main__': # pragma: no cover
    parser = argparse.ArgumentParser(
        description='Find prices for products'
    )
    parser.add_argument(
        '-m', '--metroarea',
        required=True,
        type=str,
        help='Metropolitan area to search caigslist.org for'
    )
    parser.add_argument(
        '-q', '--query',
        required=True,
        type=str,
        help='Product query to find prices for.'
    )
    parser.add_argument(
        '--sold',
        action='store_true',
        help='Pass this flag to search for *sold* items.'
    )
    parser.add_argument(
        '-n',
        required=False,
        type=int,
        default=1,
        help='Number of eBay pages to search.')

    args_dict = vars(parser.parse_args())

    run_all(args_dict)