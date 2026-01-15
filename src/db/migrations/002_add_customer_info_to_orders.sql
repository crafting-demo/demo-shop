-- Migration: 002_add_customer_info_to_orders
-- Description: Add customer information fields to orders table
-- Created: 2026-01-15

ALTER TABLE orders 
ADD COLUMN customer_name VARCHAR(255) NOT NULL DEFAULT '',
ADD COLUMN customer_email VARCHAR(255) NOT NULL DEFAULT '',
ADD COLUMN shipping_address TEXT NOT NULL DEFAULT '';

-- Remove defaults after adding columns
ALTER TABLE orders 
ALTER COLUMN customer_name DROP DEFAULT,
ALTER COLUMN customer_email DROP DEFAULT,
ALTER COLUMN shipping_address DROP DEFAULT;

COMMENT ON COLUMN orders.customer_name IS 'Name of the customer who placed the order';
COMMENT ON COLUMN orders.customer_email IS 'Email address of the customer';
COMMENT ON COLUMN orders.shipping_address IS 'Shipping address for the order';
