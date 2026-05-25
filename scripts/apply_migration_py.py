"""Apply Supabase migration using Python + psycopg (psycopg-binary)

Usage: python scripts/apply_migration_py.py
Reads DB credentials from .env (SUPABASE_DB_HOST, SUPABASE_DB_PORT, SUPABASE_DB_NAME, SUPABASE_DB_USER, SUPABASE_DB_PASSWORD)
"""
from dotenv import load_dotenv
import os
import sys

load_dotenv()

PG_HOST = os.getenv('SUPABASE_DB_HOST') or os.getenv('PGHOST')
PG_PORT = os.getenv('SUPABASE_DB_PORT') or os.getenv('PGPORT') or '5432'
PG_DB   = os.getenv('SUPABASE_DB_NAME') or os.getenv('PGDATABASE')
PG_USER = os.getenv('SUPABASE_DB_USER') or os.getenv('PGUSER')
PG_PASS = os.getenv('SUPABASE_DB_PASSWORD') or os.getenv('PGPASSWORD')

if not (PG_HOST and PG_DB and PG_USER and PG_PASS):
    print('Missing DB credentials in .env. Please set SUPABASE_DB_HOST/NAME/USER/PASSWORD')
    sys.exit(2)

try:
    import psycopg
except Exception as e:
    print('psycopg not installed. Install with: python -m pip install psycopg-binary')
    print(str(e))
    sys.exit(3)

migration_path = os.path.join(os.path.dirname(__file__), '..', 'db', 'supabase_migration.sql')
migration_path = os.path.normpath(migration_path)
if not os.path.exists(migration_path):
    print('Migration file not found:', migration_path)
    sys.exit(4)

with open(migration_path, 'r', encoding='utf-8') as f:
    sql = f.read()

conn = None
try:
    conn = psycopg.connect(host=PG_HOST, port=PG_PORT, dbname=PG_DB, user=PG_USER, password=PG_PASS)
    conn.autocommit = True
    with conn.cursor() as cur:
        cur.execute(sql)
    print('MIGRATION_APPLIED')
    sys.exit(0)
except Exception as e:
    print('MIGRATION_ERROR')
    print(str(e))
    sys.exit(5)
finally:
    if conn:
        conn.close()
