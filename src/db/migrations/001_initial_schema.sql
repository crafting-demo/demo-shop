-- Migration: 001_initial_schema
-- Description: Initial database schema for the Transaction Service
-- Created: 2026-01-08

-- =============================================================================
-- Products Table (Inventory)
-- =============================================================================

CREATE TABLE products (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    description TEXT,
    image_data BYTEA,
    price_per_unit BIGINT NOT NULL CHECK (price_per_unit >= 0),
    count_in_stock INTEGER NOT NULL DEFAULT 0 CHECK (count_in_stock >= 0),
    state SMALLINT NOT NULL DEFAULT 1,
    -- State values: 0=UNSPECIFIED, 1=AVAILABLE, 2=OFF_SHELF
    is_deleted BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_products_state ON products(state) WHERE is_deleted = FALSE;
CREATE INDEX idx_products_created_at ON products(created_at) WHERE is_deleted = FALSE;

COMMENT ON TABLE products IS 'Product inventory for the shop';
COMMENT ON COLUMN products.price_per_unit IS 'Price in smallest currency unit (e.g., cents)';
COMMENT ON COLUMN products.state IS '0=UNSPECIFIED, 1=AVAILABLE, 2=OFF_SHELF';

-- =============================================================================
-- Carts Table
-- =============================================================================

CREATE TABLE carts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

COMMENT ON TABLE carts IS 'Shopping carts for customers';

-- =============================================================================
-- Cart Items Table
-- =============================================================================

CREATE TABLE cart_items (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    cart_id UUID NOT NULL REFERENCES carts(id) ON DELETE CASCADE,
    product_id UUID NOT NULL REFERENCES products(id) ON DELETE RESTRICT,
    quantity INTEGER NOT NULL CHECK (quantity > 0),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE(cart_id, product_id)
);

CREATE INDEX idx_cart_items_cart_id ON cart_items(cart_id);
CREATE INDEX idx_cart_items_product_id ON cart_items(product_id);

COMMENT ON TABLE cart_items IS 'Items in shopping carts';

-- =============================================================================
-- Orders Table
-- =============================================================================

CREATE TABLE orders (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    total_amount BIGINT NOT NULL CHECK (total_amount >= 0),
    state SMALLINT NOT NULL DEFAULT 1,
    -- State values: 0=UNSPECIFIED, 1=PROCESSING, 2=SHIPPED, 3=COMPLETED, 4=CANCELED
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_orders_state ON orders(state);
CREATE INDEX idx_orders_created_at ON orders(created_at);

COMMENT ON TABLE orders IS 'Customer orders';
COMMENT ON COLUMN orders.total_amount IS 'Total amount in smallest currency unit (e.g., cents)';
COMMENT ON COLUMN orders.state IS '0=UNSPECIFIED, 1=PROCESSING, 2=SHIPPED, 3=COMPLETED, 4=CANCELED';

-- =============================================================================
-- Order Items Table
-- =============================================================================

CREATE TABLE order_items (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    order_id UUID NOT NULL REFERENCES orders(id) ON DELETE CASCADE,
    product_id UUID NOT NULL REFERENCES products(id) ON DELETE RESTRICT,
    -- Product snapshot at time of purchase
    product_name VARCHAR(255) NOT NULL,
    product_description TEXT,
    product_image_data BYTEA,
    quantity INTEGER NOT NULL CHECK (quantity > 0),
    price_at_purchase BIGINT NOT NULL CHECK (price_at_purchase >= 0),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_order_items_order_id ON order_items(order_id);
CREATE INDEX idx_order_items_product_id ON order_items(product_id);

COMMENT ON TABLE order_items IS 'Items in orders with product snapshot at purchase time';
COMMENT ON COLUMN order_items.price_at_purchase IS 'Price per unit at time of order creation';

-- =============================================================================
-- Trigger Functions for updated_at
-- =============================================================================

CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_products_updated_at
    BEFORE UPDATE ON products
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER trigger_carts_updated_at
    BEFORE UPDATE ON carts
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER trigger_cart_items_updated_at
    BEFORE UPDATE ON cart_items
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER trigger_orders_updated_at
    BEFORE UPDATE ON orders
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();
