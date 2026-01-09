#!/bin/bash

# Database Migration Script
# Runs SQL migrations from src/db/migrations directory

SRC_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
MIGRATIONS_DIR="$SRC_DIR/src/db/migrations"

# Database configuration (with defaults)
DB_HOST="${DB_HOST:-localhost}"
DB_PORT="${DB_PORT:-5432}"
DB_USER="${DB_USER:-postgres}"
DB_PASSWORD="${DB_PASSWORD:-postgres}"
DB_NAME="${DB_NAME:-demoshop}"
DB_SSLMODE="${DB_SSLMODE:-disable}"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to execute SQL
execute_sql() {
    local sql="$1"
    PGPASSWORD="$DB_PASSWORD" psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" -c "$sql" -q
}

# Function to execute SQL file
execute_sql_file() {
    local file="$1"
    PGPASSWORD="$DB_PASSWORD" psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" -f "$file" -q
}

# Function to check if a migration has been applied
is_migration_applied() {
    local migration_name="$1"
    local result=$(PGPASSWORD="$DB_PASSWORD" psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" \
        -t -c "SELECT COUNT(*) FROM schema_migrations WHERE migration_name = '$migration_name';" 2>/dev/null || echo "0")
    result=$(echo "$result" | tr -d '[:space:]')
    [ "$result" != "0" ]
}

# Function to record a migration
record_migration() {
    local migration_name="$1"
    execute_sql "INSERT INTO schema_migrations (migration_name, applied_at) VALUES ('$migration_name', NOW());"
}

# Check if psql is available
if ! command -v psql &> /dev/null; then
    print_error "psql command not found. Please install PostgreSQL client."
    exit 1
fi

# Check if migrations directory exists
if [ ! -d "$MIGRATIONS_DIR" ]; then
    print_error "Migrations directory not found: $MIGRATIONS_DIR"
    exit 1
fi

print_info "Connecting to PostgreSQL database..."
print_info "Host: $DB_HOST:$DB_PORT"
print_info "Database: $DB_NAME"
print_info "User: $DB_USER"

# Test database connection
if ! PGPASSWORD="$DB_PASSWORD" psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" -c "SELECT 1;" > /dev/null 2>&1; then
    print_error "Failed to connect to database. Please check your connection settings."
    exit 1
fi

print_info "Database connection successful!"

# Create migrations tracking table if it doesn't exist
print_info "Creating schema_migrations table if not exists..."
execute_sql "CREATE TABLE IF NOT EXISTS schema_migrations (
    id SERIAL PRIMARY KEY,
    migration_name VARCHAR(255) NOT NULL UNIQUE,
    applied_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);" || {
    print_error "Failed to create schema_migrations table"
    exit 1
}

# Find all migration files
print_info "Scanning for migration files..."
migration_files=($(find "$MIGRATIONS_DIR" -maxdepth 1 -name "*.sql" -type f | sort))

if [ ${#migration_files[@]} -eq 0 ]; then
    print_warn "No migration files found in $MIGRATIONS_DIR"
    exit 0
fi

print_info "Found ${#migration_files[@]} migration file(s)"

# Apply migrations
applied_count=0
skipped_count=0

for migration_file in "${migration_files[@]}"; do
    migration_name=$(basename "$migration_file")
    
    if is_migration_applied "$migration_name"; then
        print_info "⏭️  Skipping $migration_name (already applied)"
        ((skipped_count++))
        continue
    fi
    
    print_info "▶️  Applying migration: $migration_name"
    
    if execute_sql_file "$migration_file"; then
        record_migration "$migration_name"
        print_info "✅ Successfully applied: $migration_name"
        ((applied_count++))
    else
        print_error "❌ Failed to apply migration: $migration_name"
        exit 1
    fi
done

# Summary
echo ""
print_info "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
print_info "Migration Summary:"
print_info "  Applied: $applied_count"
print_info "  Skipped: $skipped_count"
print_info "  Total:   ${#migration_files[@]}"
print_info "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

if [ $applied_count -gt 0 ]; then
    print_info "🎉 Database migrations completed successfully!"
else
    print_info "✨ Database is up to date!"
fi
