import React, { useState } from 'react';
import { useMutation } from '@apollo/client';
import { PLACE_ORDER } from '../queries';
import { PlaceOrderMutation, PlaceOrderMutationVariables } from '../../generated/graphql';
import { useTheme } from '../../shared/ThemeContext';
import './PaymentPage.css';

interface PaymentPageProps {
  totalPrice: number; // in cents
  onPlaceOrder: () => void;
  onBack: () => void;
}

interface CustomerInfo {
  name: string;
  email: string;
  shippingAddress: string;
}

const PaymentPage: React.FC<PaymentPageProps> = ({
  totalPrice,
  onPlaceOrder,
  onBack,
}) => {
  const { theme, toggleTheme } = useTheme();
  const [customerInfo, setCustomerInfo] = useState<CustomerInfo>({
    name: '',
    email: '',
    shippingAddress: '',
  });

  const [errors, setErrors] = useState<Partial<CustomerInfo>>({});

  const [placeOrder, { loading }] = useMutation<PlaceOrderMutation, PlaceOrderMutationVariables>(
    PLACE_ORDER
  );

  const validateForm = (): boolean => {
    const newErrors: Partial<CustomerInfo> = {};

    if (!customerInfo.name.trim()) {
      newErrors.name = 'Name is required';
    }

    if (!customerInfo.email.trim()) {
      newErrors.email = 'Email is required';
    } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(customerInfo.email)) {
      newErrors.email = 'Invalid email format';
    }

    if (!customerInfo.shippingAddress.trim()) {
      newErrors.shippingAddress = 'Shipping address is required';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (validateForm()) {
      try {
        await placeOrder({
          variables: {
            input: {
              customerName: customerInfo.name,
              customerEmail: customerInfo.email,
              shippingAddress: customerInfo.shippingAddress,
            },
          },
        });
        onPlaceOrder();
      } catch (error) {
        console.error('Error placing order:', error);
        alert('Failed to place order. Please try again.');
      }
    }
  };

  const handleChange = (field: keyof CustomerInfo, value: string) => {
    setCustomerInfo(prev => ({ ...prev, [field]: value }));
    if (errors[field]) {
      setErrors(prev => ({ ...prev, [field]: undefined }));
    }
  };

  return (
    <div className="payment-page">
      <header className="header">
        <button className="btn btn-secondary" onClick={onBack}>
          ← Back
        </button>
        <h1>Payment</h1>
        <button className="theme-toggle" onClick={toggleTheme} title="Toggle theme">
          {theme === 'light' ? '🌙 Dark' : '☀️ Light'}
        </button>
      </header>

      <div className="container">
        <form className="payment-form card" onSubmit={handleSubmit}>
          <h2>Customer Information</h2>

          <div className="form-group">
            <label className="form-label">
              Name <span className="required">*</span>
            </label>
            <input
              type="text"
              className="form-input"
              value={customerInfo.name}
              onChange={e => handleChange('name', e.target.value)}
            />
            {errors.name && <p className="error-message">{errors.name}</p>}
          </div>

          <div className="form-group">
            <label className="form-label">
              Email <span className="required">*</span>
            </label>
            <input
              type="email"
              className="form-input"
              value={customerInfo.email}
              onChange={e => handleChange('email', e.target.value)}
            />
            {errors.email && <p className="error-message">{errors.email}</p>}
          </div>

          <div className="form-group">
            <label className="form-label">
              Shipping Address <span className="required">*</span>
            </label>
            <textarea
              className="form-input"
              rows={4}
              value={customerInfo.shippingAddress}
              onChange={e => handleChange('shippingAddress', e.target.value)}
            />
            {errors.shippingAddress && (
              <p className="error-message">{errors.shippingAddress}</p>
            )}
          </div>

          <div className="payment-summary">
            <h2>Payment Summary</h2>
            <div className="summary-row">
              <span>Total:</span>
              <span className="total-price">${(totalPrice / 100).toFixed(2)}</span>
            </div>
          </div>

          <button type="submit" className="btn btn-primary place-order-btn" disabled={loading}>
            {loading ? 'Placing Order...' : 'Place Order'}
          </button>
        </form>
      </div>
    </div>
  );
};

export default PaymentPage;
