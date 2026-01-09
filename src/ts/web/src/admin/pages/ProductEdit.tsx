import React, { useState } from 'react';
import { Product } from '../../shared/types';
import './ProductEdit.css';

interface ProductEditProps {
  product: Product;
  onSave: (product: Product) => void;
  onCancel: () => void;
  onRemove: (productId: string) => void;
}

const ProductEdit: React.FC<ProductEditProps> = ({
  product,
  onSave,
  onCancel,
  onRemove,
}) => {
  const [editedProduct, setEditedProduct] = useState<Product>({ ...product });
  const [hasChanges, setHasChanges] = useState(false);

  const handleChange = (field: keyof Product, value: any) => {
    setEditedProduct(prev => ({ ...prev, [field]: value }));
    setHasChanges(true);
  };

  const handleSave = () => {
    onSave(editedProduct);
  };

  const handleToggleState = () => {
    const newState = editedProduct.state === 'AVAILABLE' ? 'OFF_SHELF' : 'AVAILABLE';
    setEditedProduct(prev => ({ ...prev, state: newState }));
    setHasChanges(true);
  };

  const handleRemove = () => {
    if (window.confirm(`Are you sure you want to remove ${editedProduct.name}?`)) {
      onRemove(editedProduct.id);
    }
  };

  return (
    <div className="product-edit">
      <div className="page-header">
        <h1>Edit Product</h1>
        <div className="header-actions">
          <button className="btn btn-secondary" onClick={onCancel}>
            Cancel
          </button>
          <button
            className="btn btn-primary"
            onClick={handleSave}
            disabled={!hasChanges}
          >
            Save
          </button>
        </div>
      </div>

      <div className="edit-form card">
        <div className="form-section">
          <h2>Product Information</h2>

          <div className="form-group">
            <label className="form-label">Product ID</label>
            <input
              type="text"
              className="form-input"
              value={editedProduct.id}
              disabled
            />
          </div>

          <div className="form-group">
            <label className="form-label">Product Name</label>
            <input
              type="text"
              className="form-input"
              value={editedProduct.name}
              onChange={e => handleChange('name', e.target.value)}
            />
          </div>

          <div className="form-group">
            <label className="form-label">Description</label>
            <textarea
              className="form-input"
              rows={4}
              value={editedProduct.description || ''}
              onChange={e => handleChange('description', e.target.value)}
            />
          </div>

          <div className="form-group">
            <label className="form-label">Image Data</label>
            <input
              type="text"
              className="form-input"
              value={editedProduct.imageData || ''}
              onChange={e => handleChange('imageData', e.target.value)}
            />
            <div className="image-preview">
              <img src={editedProduct.imageData || ''} alt={editedProduct.name} />
            </div>
          </div>

          <div className="form-row">
            <div className="form-group">
              <label className="form-label">Price per unit ($)</label>
              <input
                type="number"
                className="form-input"
                value={(editedProduct.pricePerUnit / 100).toFixed(2)}
                onChange={e => handleChange('pricePerUnit', Math.round(Number(e.target.value) * 100))}
                step="0.01"
                min="0"
              />
            </div>

            <div className="form-group">
              <label className="form-label">Count in stock</label>
              <input
                type="number"
                className="form-input"
                value={editedProduct.countInStock}
                onChange={e => handleChange('countInStock', Number(e.target.value))}
                min="0"
              />
            </div>
          </div>

          <div className="form-group">
            <label className="form-label">State</label>
            <div className="state-control">
              <span className={`state-badge ${editedProduct.state.toLowerCase()}`}>
                {editedProduct.state === 'AVAILABLE' ? 'Available' : 'Off-shelf'}
              </span>
              <button className="btn btn-secondary" onClick={handleToggleState}>
                {editedProduct.state === 'AVAILABLE'
                  ? 'Move Off-shelf'
                  : 'Move to Available'}
              </button>
            </div>
          </div>
        </div>

        <div className="form-actions">
          <button className="btn btn-danger" onClick={handleRemove}>
            Remove Product
          </button>
        </div>
      </div>
    </div>
  );
};

export default ProductEdit;
