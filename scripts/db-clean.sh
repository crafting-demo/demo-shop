#!/bin/bash

# Remove everything from the database.

. "$(dirname "${BASH_SOURCE[0]}")/db-funcs.sh"

execute_sql "DO \$\$ DECLARE
    r RECORD;
BEGIN
    FOR r IN (SELECT tablename FROM pg_tables WHERE schemaname = 'public') LOOP
        EXECUTE 'DROP TABLE IF EXISTS ' || quote_ident(r.tablename) || ' CASCADE';
    END LOOP;
END \$\$;"
