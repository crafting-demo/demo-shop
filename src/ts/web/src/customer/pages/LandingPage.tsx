import React, { useRef, useEffect } from 'react';
import { useQuery } from '@apollo/client';
import { Product } from '../../shared/types';
import { GET_PRODUCTS } from '../queries';
import { GetProductsQuery, GetProductsQueryVariables } from '../../generated/graphql';
import { getImageUrl } from '../../shared/helpers';
import DarkModeToggle from '../../shared/DarkModeToggle';
import './LandingPage.css';

interface LandingPageProps {
  cartItemCount: number;
  onProductClick: (product: Product) => void;
  onCartClick: () => void;
}

const LandingPage: React.FC<LandingPageProps> = ({
  cartItemCount,
  onProductClick,
  onCartClick,
}) => {
  const observerTarget = useRef<HTMLDivElement>(null);

  const { data, loading, fetchMore } = useQuery<GetProductsQuery, GetProductsQueryVariables>(
    GET_PRODUCTS,
    {
      variables: { first: 20 },
    }
  );

  const products = data?.products.edges.map(edge => edge.node) || [];
  const hasNextPage = data?.products.pageInfo.hasNextPage || false;
  const endCursor = data?.products.pageInfo.endCursor;

  useEffect(() => {
    const observer = new IntersectionObserver(
      entries => {
        if (entries[0].isIntersecting && hasNextPage && !loading) {
          fetchMore({
            variables: {
              first: 20,
              after: endCursor,
            },
          });
        }
      },
      { threshold: 0.1 }
    );

    if (observerTarget.current) {
      observer.observe(observerTarget.current);
    }

    return () => {
      if (observerTarget.current) {
        observer.unobserve(observerTarget.current);
      }
    };
  }, [hasNextPage, loading, endCursor, fetchMore]);

  return (
    <div className="landing-page">
      <header className="header">
        <h1>Shop</h1>
        <div className="header-actions">
          <DarkModeToggle />
          <button className="cart-button" onClick={onCartClick}>
            <span className="cart-icon">🛒</span>
            {cartItemCount > 0 && (
              <span className="cart-badge">{cartItemCount}</span>
            )}
          </button>
        </div>
      </header>

      <div className="container">
        {loading && products.length === 0 ? (
          <div className="loading">Loading products...</div>
        ) : (
          <>
            <div className="product-grid">
              {products.map(product => (
                <div
                  key={product.id}
                  className="product-card card"
                  onClick={() => onProductClick(product)}
                >
                  <img src={getImageUrl(product.imageData)} alt={product.name} />
                  <h3>{product.name}</h3>
                  <p className="price">${(product.pricePerUnit / 100).toFixed(2)}</p>
                  <p className="stock">In stock: {product.countInStock}</p>
                </div>
              ))}
            </div>
            {hasNextPage && <div ref={observerTarget} className="observer-target" />}
          </>
        )}
      </div>
    </div>
  );
};

export default LandingPage;
