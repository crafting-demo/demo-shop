#!/bin/bash

# Database Example Data Loading Script
# Loads example data from src/db/examples directory

. "$(dirname "${BASH_SOURCE[0]}")/db-funcs.sh"

# Check if psql is available
command -v psql &> /dev/null || fatal "psql command not found. Please install PostgreSQL client."

# Check if examples directory exists
[[ -d "$EXAMPLES_DIR" ]] || fatal "Examples directory not found: $EXAMPLES_DIR"

print_info "Connecting to PostgreSQL database..."
print_info "Host: $DB_HOST:$DB_PORT"
print_info "Database: $DB_NAME"
print_info "User: $DB_USER"

# Test database connection
execute_sql 'SELECT 1;' >/dev/null 2>&1 || fatal "Failed to connect to database. Please check your connection settings."

print_info "Database connection successful!"

# Find all example data files
print_info "Scanning for example data files..."
example_files=($(find "$EXAMPLES_DIR" -maxdepth 1 -name "*.sql" -type f | sort))

if [ ${#example_files[@]} -eq 0 ]; then
    print_warn "No example data files found in $EXAMPLES_DIR"
    exit 0
fi

print_info "Found ${#example_files[@]} example data file(s)"

# Load example data
loaded_count=0

for example_file in "${example_files[@]}"; do
    example_name=$(basename "$example_file")
    
    print_info "▶️  Loading example data: $example_name"
    
    execute_sql_file "$example_file" || fatal "❌ Failed to load example data: $example_name"
    
    print_info "✅ Successfully loaded: $example_name"
    ((loaded_count++))
done

# Summary
echo ""
print_info "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
print_info "Example Data Loading Summary:"
print_info "  Loaded: $loaded_count"
print_info "  Total:  ${#example_files[@]}"
print_info "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

if [ $loaded_count -gt 0 ]; then
    print_info "🎉 Example data loaded successfully!"
else
    print_info "✨ No example data to load!"
fi
