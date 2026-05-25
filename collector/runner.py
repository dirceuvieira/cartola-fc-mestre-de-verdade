"""Runner script to invoke HTTP collector PoC.

This provides a safe CLI entrypoint that uses the fetch module with a configured Session.
"""
import os
import logging
import argparse
from collector.fetch import run_collect
from collector.single_run import setup_http_session

LOG = logging.getLogger('collector.runner')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--db', default='data/coletor.db', help='SQLite DB path')
    parser.add_argument('--base-url', default=os.environ.get('CARTOLA_BASE_URL', 'https://api.cartola.globo.com'), help='Cartola base URL')
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO)
    session = setup_http_session()
    run_collect(args.db, args.base_url, session)


if __name__ == '__main__':
    main()
