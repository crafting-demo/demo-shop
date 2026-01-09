import React from 'react';
import './ThankYouPage.css';

interface ThankYouPageProps {
  onContinueShopping: () => void;
}

const ThankYouPage: React.FC<ThankYouPageProps> = ({ onContinueShopping }) => {
  return (
    <div className="thankyou-page">
      <div className="container">
        <div className="thankyou-card card">
          <div className="success-icon">✓</div>
          <h1>Thank You!</h1>
          <p>Your order has been placed successfully.</p>
          <p className="subtitle">
            We'll send you a confirmation email shortly.
          </p>
          <button
            className="btn btn-primary continue-btn"
            onClick={onContinueShopping}
          >
            Continue Shopping
          </button>
        </div>
      </div>
    </div>
  );
};

export default ThankYouPage;
