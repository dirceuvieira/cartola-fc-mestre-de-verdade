<#
Apply Supabase migration using psql CLI (PowerShell)

Usage examples (PowerShell):
# Set credentials as environment variables (preferred for CI):
$env:SUPABASE_DB_HOST = "your-db-host.supabase.co"
$env:SUPABASE_DB_PORT = "5432"
$env:SUPABASE_DB_NAME = "postgres"
$env:SUPABASE_DB_USER = "postgres"
$env:SUPABASE_DB_PASSWORD = "your-password"

# Run script from repository root:
.\scripts\apply_supabase_migration.ps1

Parameters:
- MigrationPath: path to SQL file relative to repo root (default: db\supabase_migration.sql)
- WhatIf: if passed, prints the psql command that would run (no execution)

Notes:
- Requires psql in PATH. On Windows install Postgres client or use psql bundled with Postgres.
- The script sets PGPASSWORD in the environment for the duration of the psql process.
- For CI, prefer storing SUPABASE_DB_* secrets in the runner and not in plaintext.
#>

param(
    [string]$MigrationPath = "db\supabase_migration.sql",
    [switch]$WhatIf
)

$scriptRoot = Split-Path -Parent $MyInvocation.MyCommand.Definition
$repoRoot = Resolve-Path "$scriptRoot\.." | Select-Object -ExpandProperty Path
$migrationFull = Join-Path $repoRoot $MigrationPath

if (-not (Test-Path $migrationFull)) {
    Write-Error "Migration file not found: $migrationFull"
    exit 1
}

# Resolve credentials from SUPABASE_DB_* or PG* env vars
$pgHost = $env:SUPABASE_DB_HOST -or $env:PGHOST
$pgPort = $env:SUPABASE_DB_PORT -or $env:PGPORT -or "5432"
$pgDb   = $env:SUPABASE_DB_NAME -or $env:PGDATABASE
$pgUser = $env:SUPABASE_DB_USER -or $env:PGUSER
$pgPass = $env:SUPABASE_DB_PASSWORD -or $env:PGPASSWORD

if (-not $pgHost -or -not $pgDb -or -not $pgUser -or -not $pgPass) {
    Write-Host "Missing DB credentials. Please set SUPABASE_DB_HOST/NAME/USER/PASSWORD environment variables or PGHOST/PGDATABASE/PGUSER/PGPASSWORD." -ForegroundColor Yellow
    exit 2
}

# Check for psql
$psql = Get-Command psql -ErrorAction SilentlyContinue
if (-not $psql) {
    Write-Host "psql not found in PATH. Please install PostgreSQL client or add psql to PATH." -ForegroundColor Red
    exit 3
}

$cmd = "psql -h $pgHost -p $pgPort -U $pgUser -d $pgDb -f `"$migrationFull`""

if ($WhatIf) {
    Write-Host "[WhatIf] Would run: $cmd"
    exit 0
}

# Run psql with PGPASSWORD set for this process only
$env:PGPASSWORD = $pass
try {
    Write-Host ("Applying migration: {0} to {1}@{2}:{3}/{4}" -f $migrationFull, $pgUser, $pgHost, $pgPort, $pgDb)
        & psql -h $pgHost -p $pgPort -U $pgUser -d $pgDb -f $migrationFull
    $exit = $LASTEXITCODE
    if ($exit -ne 0) {
        Write-Error "psql exited with code $exit"
        exit $exit
    }
    Write-Host "Migration applied successfully." -ForegroundColor Green
} finally {
    Remove-Item Env:PGPASSWORD -ErrorAction SilentlyContinue
}
