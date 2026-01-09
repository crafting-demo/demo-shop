# Database Example Data

This directory contains SQL scripts that populate the database with example data for testing and demonstration purposes.

## Files

- `001_example_products.sql` - Inserts 25 example products into the inventory

## Usage

These scripts are designed to be idempotent - they can be run multiple times without creating duplicate data. Each script uses `ON CONFLICT DO NOTHING` to skip records that already exist.

### Running the Scripts

You can run these scripts using `psql` or any PostgreSQL client:

```bash
psql -U your_username -d your_database -f 001_example_products.sql
```

Or from within a PostgreSQL session:

```sql
\i 001_example_products.sql
```

## Example Products

The example products include a diverse range of categories:

- **Electronics** (Blue): Headphones, smartwatches, speakers, webcams
- **Home & Office** (Brown): Office chairs, desk lamps, keyboards
- **Books & Media** (Orange): Programming books
- **Sports & Outdoors** (Green): Yoga mats, water bottles, running shoes
- **Fashion & Accessories** (Purple): Backpacks, sunglasses, watches
- **Kitchen & Dining** (Red): Coffee makers, knife sets, cookware
- **Personal Care** (Teal): Electric toothbrushes, hair dryers
- **Gaming** (Magenta): Gaming mice, gaming headsets
- **Special Items** (Gold): Vintage record players, camera tripods, espresso machines

All products have:
- Realistic prices (stored in cents)
- Varying stock levels (from low stock to high stock)
- Detailed descriptions
- Appropriate state (AVAILABLE or OFF_SHELF)
- **Product images**: Small 100x100px PNG placeholder images with category-specific colors (base64-encoded)

## Product Images

Each product includes a small placeholder image (100x100 pixels) stored as BYTEA in the database. Images are encoded as base64 strings in the SQL and decoded using PostgreSQL's `decode()` function during insertion.

The placeholder images are simple colored PNG squares that help distinguish product categories:
- Electronics: Blue (#3B82F6)
- Home & Office: Brown (#92400E)
- Books & Media: Orange (#EA580C)
- Sports & Outdoors: Green (#16A34A)
- Fashion & Accessories: Purple (#9333EA)
- Kitchen & Dining: Red (#DC2626)
- Personal Care: Teal (#0D9488)
- Gaming: Magenta (#C026D3)
- Premium/Limited Stock: Gold (#CA8A04)
- Off-Shelf: Gray (#6B7280)

## Product States

- `1` = AVAILABLE - Product is available for purchase
- `2` = OFF_SHELF - Product is temporarily unavailable
