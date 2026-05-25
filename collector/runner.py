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
    parser.add_argument('--use-supabase', action='store_true', help='Write results to Supabase instead of local SQLite')
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO)
    session = setup_http_session()

    supabase_writer = None
    if args.use_supabase:
        from collector.supabase_client import create_supabase_client, SupabaseWriter
        supabase_url = os.environ.get('SUPABASE_URL')
        supabase_key = os.environ.get('SUPABASE_KEY')
        if not supabase_url or not supabase_key:
            LOG.error('SUPABASE_URL and SUPABASE_KEY must be set when --use-supabase is provided')
            return
        client = create_supabase_client(supabase_url, supabase_key)
        supabase_writer = SupabaseWriter(client)

    run_collect(args.db, args.base_url, session, supabase_writer)


if __name__ == '__main__':
    main()
