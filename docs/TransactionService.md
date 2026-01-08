# Transaction Service

This is a backend service exposing gRPC APIs for managing Inventory, Carts and Orders.

## Inventory APIs

- Query Products with pagination support;
- Create Product: adding a new product into the Inventory;
- Update Product: update an existing product;
- Delete Product: mark the product as deleted, so it will be excluded from Query Products API.

## Cart APIs

A Cart is automatically created based on a client ID which is generated automatically according
to the information from the client side.

- Add Product to Cart: add a Product (referenced by id) to the Cart (specified by Cart id);
- Update Product in the Cart: changing the quantity. If quantity is zero, it's removed.

## Order APIs

- Create Order: convert a Cart (specified by Cart id) into an order;
- Query Orders with pagination support;
- Update Order: update the state of the order.
