from dotenv import load_dotenv
import os
import sys
import shutil

load_dotenv()

SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_KEY')

if SUPABASE_URL and SUPABASE_KEY:
    try:
        from supabase import create_client
        client = create_client(SUPABASE_URL, SUPABASE_KEY)
        # Try a lightweight request: list first row of atletas
        res = client.table('atletas').select('id').limit(1).execute()
        # res may have .data or .get('data') depending on client; handle both
        data = None
        try:
            data = res.data
        except Exception:
            try:
                data = res.get('data')
            except Exception:
                data = None
        print('SUPABASE_OK')
        print('rows:', len(data) if data else 0)
        sys.exit(0)
    except Exception as e:
        print('SUPABASE_ERROR')
        print(str(e))
        sys.exit(2)

# Fallback: try direct Postgres with psql
PG_HOST = os.getenv('SUPABASE_DB_HOST') or os.getenv('PGHOST')
PG_PORT = os.getenv('SUPABASE_DB_PORT') or os.getenv('PGPORT') or '5432'
PG_DB   = os.getenv('SUPABASE_DB_NAME') or os.getenv('PGDATABASE')
PG_USER = os.getenv('SUPABASE_DB_USER') or os.getenv('PGUSER')
PG_PASS = os.getenv('SUPABASE_DB_PASSWORD') or os.getenv('PGPASSWORD')

if PG_HOST and PG_DB and PG_USER and PG_PASS:
    psql = shutil.which('psql')
    if not psql:
        print('PSQL_MISSING')
        sys.exit(3)
    import subprocess
    env = os.environ.copy()
    env['PGPASSWORD'] = PG_PASS
    cmd = [psql, '-h', PG_HOST, '-p', str(PG_PORT), '-U', PG_USER, '-d', PG_DB, '-c', "\dt"]
    try:
        out = subprocess.check_output(cmd, env=env, stderr=subprocess.STDOUT, universal_newlines=True)
        print('PSQL_OK')
        print(out)
        sys.exit(0)
    except subprocess.CalledProcessError as e:
        print('PSQL_ERROR')
        print(e.output)
        sys.exit(4)

print('NO_CREDENTIALS')
sys.exit(1)
