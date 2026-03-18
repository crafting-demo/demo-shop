# A Demo Online Shop

This is an AI generated, multi-microservice based online shop demo.

## Quick Start

1. **Run database migrations**:
   ```bash
   ./scripts/db-migrate.sh
   ```

2. **Load example inventory data**:
   ```bash
   ./scripts/db-load-examples.sh
   ```

3. **Build and run the application**:
   ```bash
   ./scripts/build-all.sh
   ```

## Database Scripts

- `./scripts/db-migrate.sh` - Apply database schema migrations
- `./scripts/db-load-examples.sh` - Load example products into the inventory
- `./scripts/db-clean.sh` - Clean/reset the database
- `./scripts/db-shell.sh` - Open PostgreSQL shell
