import React, { useState } from 'react';
import { useQuery } from '@apollo/client';
import { Product } from '../shared/types';
import LandingPage from './pages/LandingPage';
import ProductPage from './pages/ProductPage';
import CheckoutPage from './pages/CheckoutPage';
import PaymentPage from './pages/PaymentPage';
import ThankYouPage from './pages/ThankYouPage';
import { GET_CART } from './queries';
import { GetCartQuery } from '../generated/graphql';

type Page = 'landing' | 'product' | 'checkout' | 'payment' | 'thankyou';

const CustomerApp: React.FC = () => {
  const [currentPage, setCurrentPage] = useState<Page>('landing');
  const [selectedProduct, setSelectedProduct] = useState<Product | null>(null);

  const { data: cartData, refetch: refetchCart } = useQuery<GetCartQuery>(GET_CART);

  const cart = cartData?.cart;
  const cartItemCount = cart?.items.reduce((sum, item) => sum + item.quantity, 0) || 0;

  const handleProductClick = (product: Product) => {
    setSelectedProduct(product);
    setCurrentPage('product');
  };

  const handleAddToCart = async () => {
    await refetchCart();
  };

  const handleGoToCheckout = () => {
    setCurrentPage('checkout');
  };

  const handleGoToPayment = () => {
    setCurrentPage('payment');
  };

  const handlePlaceOrder = async () => {
    await refetchCart();
    setCurrentPage('thankyou');
  };

  const handleBackToLanding = () => {
    setSelectedProduct(null);
    setCurrentPage('landing');
  };

  const handleCloseProductPage = () => {
    setSelectedProduct(null);
    setCurrentPage('landing');
  };

  const handleUpdateQuantity = async () => {
    await refetchCart();
  };

  return (
    <div>
      {currentPage === 'landing' && (
        <LandingPage
          cartItemCount={cartItemCount}
          onProductClick={handleProductClick}
          onCartClick={handleGoToCheckout}
        />
      )}
      {currentPage === 'product' && selectedProduct && (
        <ProductPage
          product={selectedProduct}
          onAddToCart={handleAddToCart}
          onClose={handleCloseProductPage}
        />
      )}
      {currentPage === 'checkout' && cart && (
        <CheckoutPage
          cart={cart}
          onUpdateQuantity={handleUpdateQuantity}
          onCheckout={handleGoToPayment}
          onBack={handleBackToLanding}
        />
      )}
      {currentPage === 'payment' && cart && (
        <PaymentPage
          totalPrice={cart.totalPrice}
          onPlaceOrder={handlePlaceOrder}
          onBack={() => setCurrentPage('checkout')}
        />
      )}
      {currentPage === 'thankyou' && (
        <ThankYouPage onContinueShopping={handleBackToLanding} />
      )}
    </div>
  );
};

export default CustomerApp;
