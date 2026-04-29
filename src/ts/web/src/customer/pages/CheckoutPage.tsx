import React from 'react';
import { useMutation } from '@apollo/client';
import { Cart } from '../../shared/types';
import { UPDATE_CART_ITEM, REMOVE_FROM_CART } from '../queries';
import {
  UpdateCartItemMutation,
  UpdateCartItemMutationVariables,
  RemoveFromCartMutation,
  RemoveFromCartMutationVariables,
} from '../../generated/graphql';
import { getImageUrl } from '../../shared/helpers';
import DarkModeToggle from '../../shared/DarkModeToggle';
import './CheckoutPage.css';

interface CheckoutPageProps {
  cart: Cart;
  onUpdateQuantity: () => void;
  onCheckout: () => void;
  onBack: () => void;
}

const CheckoutPage: React.FC<CheckoutPageProps> = ({
  cart,
  onUpdateQuantity,
  onCheckout,
  onBack,
}) => {
  const [updateCartItem] = useMutation<UpdateCartItemMutation, UpdateCartItemMutationVariables>(
    UPDATE_CART_ITEM
  );
  const [removeFromCart] = useMutation<RemoveFromCartMutation, RemoveFromCartMutationVariables>(
    REMOVE_FROM_CART
  );

  const handleUpdateQuantity = async (productId: string, quantity: number) => {
    try {
      if (quantity <= 0) {
        await removeFromCart({ variables: { productId } });
      } else {
        await updateCartItem({
          variables: {
            input: { productId, quantity },
          },
        });
      }
      onUpdateQuantity();
    } catch (error) {
      console.error('Error updating cart:', error);
    }
  };

  return (
    <div className="checkout-page">
      <header className="checkout-header">
        <button className="btn btn-secondary" onClick={onBack}>
          ← Back
        </button>
        <h1>Shopping Cart</h1>
        <div className="checkout-header-actions">
          <DarkModeToggle />
        </div>
      </header>

      <div className="container">
        {cart.items.length === 0 ? (
          <div className="empty-cart">
            <p>Your cart is empty</p>
            <button className="btn btn-primary" onClick={onBack}>
              Continue Shopping
            </button>
          </div>
        ) : (
          <>
            <div className="cart-items">
              {cart.items.map(item => (
                <div key={item.product.id} className="cart-item card">
                  <img src={getImageUrl(item.product.imageData)} alt={item.product.name} />
                  <div className="item-info">
                    <h3>{item.product.name}</h3>
                    <p className="price">${(item.product.pricePerUnit / 100).toFixed(2)} per unit</p>
                  </div>
                  <div className="quantity-controls">
                    <button
                      onClick={() => handleUpdateQuantity(item.product.id, item.quantity - 1)}
                    >
                      -
                    </button>
                    <span>{item.quantity}</span>
                    <button
                      onClick={() => handleUpdateQuantity(item.product.id, item.quantity + 1)}
                      disabled={item.quantity >= item.product.countInStock}
                    >
                      +
                    </button>
                  </div>
                  <div className="item-total">
                    <p>${(item.totalPrice / 100).toFixed(2)}</p>
                  </div>
                </div>
              ))}
            </div>

            <div className="cart-summary card">
              <h2>Order Summary</h2>
              <div className="summary-row">
                <span>Total:</span>
                <span className="total-price">${(cart.totalPrice / 100).toFixed(2)}</span>
              </div>
              <button className="btn btn-primary checkout-btn" onClick={onCheckout}>
                Proceed to Checkout
              </button>
            </div>
          </>
        )}
      </div>
    </div>
  );
};

export default CheckoutPage;
