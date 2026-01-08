# The API Demo App

This is an online shop App providing the access for Customers and Admins.

For Customers, the [Landing Page](#landing-page) will show the Inventory of products.
A customer is able to add products to the Shopping Cart, and later place an Order via the Checkout process.

For Admins, a separate endpoint should be used for viewing and editing the Inventory and Orders.

## User Flows

### Customer Flows

#### Landing Page

The public facing endpoint `shop` serves the web pages of the App.

A Customer visiting the page will see a list view of Products each represented in a form of a Card.
Inside a Product Card, there are information of:
- Product Image
- Product Name
- Price per unit
- Count in stock

There can be a number of Product Cards displayed in a row based on the width of view and multiple rows are displayed.
When the Customer scrolls down, more rows are automatically added if there's more.

When the Customer clicks on a Product Card, a [Product Page](#product-page) pops up.

On the right-top, there's a Shopping Cart icon, by clicking which, the Customer is directed to the [Checkout Page](#checkout-page).

#### Product Page

The Product Page presents more details of a selected product:
- Product Image (on the left)
- Product Name and Description (on the right side of the Product Image), Name above Description.
- Price per unit and Count in stock after the Description
- A button of "Add to Cart", when clicked, the product will be added to the "Shopping Cart".

#### Checkout Page

The Checkout Page shows a list of products in the "Shopping Cart", one per row, with following information:
- Product Image
- Product Name
- Price per unit
- Count of units in the Cart
- Total price of the products

After the list, there's a summary of total price to pay for all products in the cart.
After the summary, there's a "Checkout" button, when clicked, the Customer is directed to the [Payment Page](#payment-page).

#### Payment Page

The Payment Page asks for the Customer's detailed information:
- Name (required)
- Email (required)
- Shipping Address (required)

And a payment summary of:
- Total price

A button named "Place Order", when clicked the following operations will happen:
- An Order is created
- The Cart is cleared
- Display a "Thank you!" page with button "Continue Shopping" which will bring the Customer back to the [Landing Page](#landing-page).

### Admin Flows

Admins are expected to visit using the `admin` endpoint, which is a tabbed view:
- Left side is a menu, with items:
  - "Inventory": this will switch to the [Inventory Admin](#inventory-admin) tab;
  - "Orders": this will switch to the [Order Admin](#order-admin) tab.

#### Inventory Admin

This is a list view with each row representing a product, displaying information of:
- Product Image (small)
- Product ID (an internal unique ID)
- Product Name
- Price per unit
- Count in stock
- State: Available/Off-shelf
- Action Icon: pops up a menu to actions:
  - Edit: when clicked, showing the [Product Edit](#product-edit) page;
  - On/Off shelf: based on the current state;
  - Remove: when clicked, after confirm, remove the product from the Inventory.

The list view is paged with a user selectable page size of 10, 20, 50, 100, 200.

#### Product Edit

This is a page an Admin can edit a single product, with a form for editing:
- Product Image: can upload an image file;
- Product Name and Description
- Price per unit
- Count in stock
- State: Available/Off-shelf

The Product ID is displayed but can't be changed.
There are a few buttons for actions:
- "Save": save the current edits and go back to the [Inventory Admin](#inventory-admin) page. Disabled if no change is made;
- "On/Off Shelf": toggle the State;
- "Remove": delete the product, when clicked, after confirmation, the product is removed from the Inventory;
- "Cancel": discard any changes and go back to the [Inventory Admin](#inventory-admin) page.

#### Order Admin

This is a list view of Orders with each row representing an Order, displaying information of:
- Order ID (the unique ID per order)
- Date and Time when Order is placed
- State: Processing/Shipped/Completed/Canceled
- Total price
- Customer Name
- Customer Email
- Action icon: when clicked to pop up a menu for actions:
  - Ship: only available when the current state is Processing, and change the state to Shipped;
  - Complete: only available when the current state is Shipped, and change the state to Completed;
  - Cancel: only available when the current state is Processing or Shipped, and change the state to Canceled.

The list view is paged with a user selectable page size of 10, 20, 50, 100, 200.

## Architecture

At high level, there are:
- [Frontend service](FrontendService.md) which exposes graphQL APIs and serving static web assets;
- [Transaction service](#TransactionService.md) which is a backend exposing gRPC APIs for managing Inventory and Orders;
- [Messaging service](#MessagingService.md) which is a backend exposing gRPC APIs for sending messages to Customers and Admins.
