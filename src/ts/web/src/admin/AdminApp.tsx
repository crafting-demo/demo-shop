import React, { useState } from 'react';
import { Product } from '../shared/types';
import { useTheme } from '../shared/ThemeContext';
import InventoryAdmin from './pages/InventoryAdmin';
import ProductEdit from './pages/ProductEdit';
import OrderAdmin from './pages/OrderAdmin';
import './AdminApp.css';

type Tab = 'inventory' | 'orders';
type View = 'list' | 'edit';

const AdminApp: React.FC = () => {
  const [currentTab, setCurrentTab] = useState<Tab>('inventory');
  const [currentView, setCurrentView] = useState<View>('list');
  const [selectedProduct, setSelectedProduct] = useState<Product | null>(null);
  const { theme, toggleTheme } = useTheme();

  const handleEditProduct = (product: Product) => {
    setSelectedProduct(product);
    setCurrentView('edit');
  };

  const handleSaveProduct = () => {
    setCurrentView('list');
    setSelectedProduct(null);
  };

  const handleRemoveProduct = () => {
    setCurrentView('list');
    setSelectedProduct(null);
  };

  const handleCancelEdit = () => {
    setSelectedProduct(null);
    setCurrentView('list');
  };

  return (
    <div className="admin-app">
      <div className="sidebar">
        <h1>Admin Panel</h1>
        <nav>
          <button
            className={`nav-item ${currentTab === 'inventory' ? 'active' : ''}`}
            onClick={() => {
              setCurrentTab('inventory');
              setCurrentView('list');
            }}
          >
            Inventory
          </button>
          <button
            className={`nav-item ${currentTab === 'orders' ? 'active' : ''}`}
            onClick={() => {
              setCurrentTab('orders');
              setCurrentView('list');
            }}
          >
            Orders
          </button>
        </nav>
        <div className="sidebar-footer">
          <button
            className="theme-toggle"
            onClick={toggleTheme}
            aria-label={theme === 'dark' ? 'Switch to light mode' : 'Switch to dark mode'}
          >
            <span>{theme === 'dark' ? '\u2600\uFE0F' : '\uD83C\uDF19'}</span>
            <span className="theme-toggle-label">{theme === 'dark' ? 'Light' : 'Dark'}</span>
          </button>
        </div>
      </div>

      <div className="main-content">
        {currentTab === 'inventory' && currentView === 'list' && (
          <InventoryAdmin onEdit={handleEditProduct} />
        )}
        {currentTab === 'inventory' && currentView === 'edit' && selectedProduct && (
          <ProductEdit
            product={selectedProduct}
            onSave={handleSaveProduct}
            onCancel={handleCancelEdit}
            onRemove={handleRemoveProduct}
          />
        )}
        {currentTab === 'orders' && <OrderAdmin />}
      </div>
    </div>
  );
};

export default AdminApp;
