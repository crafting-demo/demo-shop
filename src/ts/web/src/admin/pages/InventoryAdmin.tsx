import React, { useState } from 'react';
import { useQuery, useMutation } from '@apollo/client';
import { Product } from '../../shared/types';
import { GET_PRODUCTS_ADMIN, PUT_PRODUCT_ON_SHELF, TAKE_PRODUCT_OFF_SHELF, REMOVE_PRODUCT } from '../queries';
import {
  GetProductsAdminQuery,
  GetProductsAdminQueryVariables,
  PutProductOnShelfMutation,
  PutProductOnShelfMutationVariables,
  TakeProductOffShelfMutation,
  TakeProductOffShelfMutationVariables,
  RemoveProductMutation,
  RemoveProductMutationVariables,
} from '../../generated/graphql';
import { getImageUrl } from '../../shared/helpers';
import './InventoryAdmin.css';

interface InventoryAdminProps {
  onEdit: (product: Product) => void;
}

const InventoryAdmin: React.FC<InventoryAdminProps> = ({ onEdit }) => {
  const [pageSize, setPageSize] = useState(10);
  const [currentPage, setCurrentPage] = useState(1);
  const [menuOpen, setMenuOpen] = useState<string | null>(null);

  const { data, loading, refetch } = useQuery<GetProductsAdminQuery, GetProductsAdminQueryVariables>(
    GET_PRODUCTS_ADMIN,
    {
      variables: { first: 1000 }, // Fetch all products for admin
    }
  );

  const [putProductOnShelf] = useMutation<PutProductOnShelfMutation, PutProductOnShelfMutationVariables>(
    PUT_PRODUCT_ON_SHELF
  );
  const [takeProductOffShelf] = useMutation<TakeProductOffShelfMutation, TakeProductOffShelfMutationVariables>(
    TAKE_PRODUCT_OFF_SHELF
  );
  const [removeProduct] = useMutation<RemoveProductMutation, RemoveProductMutationVariables>(
    REMOVE_PRODUCT
  );

  const products = data?.products.edges.map(edge => edge.node) || [];
  const totalPages = Math.ceil(products.length / pageSize);
  const startIndex = (currentPage - 1) * pageSize;
  const endIndex = startIndex + pageSize;
  const currentProducts = products.slice(startIndex, endIndex);

  const handleToggleState = async (product: Product) => {
    try {
      if (product.state === 'AVAILABLE') {
        await takeProductOffShelf({ variables: { id: product.id } });
      } else {
        await putProductOnShelf({ variables: { id: product.id } });
      }
      await refetch();
      setMenuOpen(null);
    } catch (error) {
      console.error('Error toggling product state:', error);
    }
  };

  const handleRemove = async (product: Product) => {
    if (window.confirm(`Are you sure you want to remove ${product.name}?`)) {
      try {
        await removeProduct({ variables: { id: product.id } });
        await refetch();
        setMenuOpen(null);
      } catch (error) {
        console.error('Error removing product:', error);
      }
    }
  };

  const toggleMenu = (productId: string) => {
    setMenuOpen(menuOpen === productId ? null : productId);
  };

  return (
    <div className="inventory-admin">
      <div className="page-header">
        <h1>Inventory Management</h1>
        <div className="page-size-selector">
          <label>Items per page:</label>
          <select
            value={pageSize}
            onChange={e => {
              setPageSize(Number(e.target.value));
              setCurrentPage(1);
            }}
          >
            <option value={10}>10</option>
            <option value={20}>20</option>
            <option value={50}>50</option>
            <option value={100}>100</option>
            <option value={200}>200</option>
          </select>
        </div>
      </div>

      {loading && products.length === 0 ? (
        <div className="loading">Loading products...</div>
      ) : (
        <div className="inventory-table">
          <div className="table-header">
            <div className="col-image">Image</div>
            <div className="col-id">ID</div>
            <div className="col-name">Name</div>
            <div className="col-price">Price</div>
            <div className="col-stock">Stock</div>
            <div className="col-state">State</div>
            <div className="col-actions">Actions</div>
          </div>

          {currentProducts.map(product => (
            <div key={product.id} className="table-row">
              <div className="col-image">
                <img src={getImageUrl(product.imageData)} alt={product.name} />
              </div>
              <div className="col-id">{product.id}</div>
              <div className="col-name">{product.name}</div>
              <div className="col-price">${(product.pricePerUnit / 100).toFixed(2)}</div>
              <div className="col-stock">{product.countInStock}</div>
              <div className="col-state">
                <span className={`state-badge ${product.state.toLowerCase()}`}>
                  {product.state === 'AVAILABLE' ? 'Available' : 'Off-shelf'}
                </span>
              </div>
              <div className="col-actions">
                <button
                  className="action-button"
                  onClick={() => toggleMenu(product.id)}
                >
                  ⋮
                </button>
                {menuOpen === product.id && (
                  <div className="action-menu">
                    <button onClick={() => onEdit(product)}>Edit</button>
                    <button onClick={() => handleToggleState(product)}>
                      {product.state === 'AVAILABLE'
                        ? 'Move Off-shelf'
                        : 'Move to Available'}
                    </button>
                    <button onClick={() => handleRemove(product)}>Remove</button>
                  </div>
                )}
              </div>
            </div>
          ))}
        </div>
      )}

      <div className="pagination">
        <button
          onClick={() => setCurrentPage(prev => Math.max(1, prev - 1))}
          disabled={currentPage === 1}
        >
          Previous
        </button>
        <span>
          Page {currentPage} of {totalPages}
        </span>
        <button
          onClick={() => setCurrentPage(prev => Math.min(totalPages, prev + 1))}
          disabled={currentPage === totalPages}
        >
          Next
        </button>
      </div>
    </div>
  );
};

export default InventoryAdmin;
