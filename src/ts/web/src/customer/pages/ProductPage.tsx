import React from 'react';
import { useMutation } from '@apollo/client';
import { Product } from '../../shared/types';
import { ADD_TO_CART } from '../queries';
import { AddToCartMutation, AddToCartMutationVariables } from '../../generated/graphql';
import { getImageUrl } from '../../shared/helpers';
import './ProductPage.css';

interface ProductPageProps {
  product: Product;
  onAddToCart: () => void;
  onClose: () => void;
}

const ProductPage: React.FC<ProductPageProps> = ({
  product,
  onAddToCart,
  onClose,
}) => {
  const [addToCart, { loading }] = useMutation<AddToCartMutation, AddToCartMutationVariables>(
    ADD_TO_CART
  );

  const handleAddToCart = async () => {
    try {
      await addToCart({
        variables: {
          input: {
            productId: product.id,
            quantity: 1,
          },
        },
      });
      onAddToCart();
      onClose();
    } catch (error) {
      console.error('Error adding to cart:', error);
    }
  };

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content product-modal" onClick={e => e.stopPropagation()}>
        <button className="close-button" onClick={onClose}>
          ✕
        </button>
        <div className="product-detail">
          <div className="product-image">
            <img src={getImageUrl(product.imageData)} alt={product.name} />
          </div>
          <div className="product-info">
            <h2>{product.name}</h2>
            <p className="description">{product.description || ''}</p>
            <div className="product-meta">
              <p className="price">${(product.pricePerUnit / 100).toFixed(2)}</p>
              <p className="stock">In stock: {product.countInStock}</p>
            </div>
            <button
              className="btn btn-primary add-to-cart-btn"
              onClick={handleAddToCart}
              disabled={product.countInStock === 0 || loading}
            >
              {loading ? 'Adding...' : 'Add to Cart'}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ProductPage;
