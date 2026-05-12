import React, { useState } from 'react';
import { Product } from '../shared/types';
import InventoryAdmin from './pages/InventoryAdmin';
import ProductEdit from './pages/ProductEdit';
import OrderAdmin from './pages/OrderAdmin';
import { useDarkMode } from '../shared/useDarkMode';
import './AdminApp.css';

type Tab = 'inventory' | 'orders';
type View = 'list' | 'edit';

const AdminApp: React.FC = () => {
  const [currentTab, setCurrentTab] = useState<Tab>('inventory');
  const [currentView, setCurrentView] = useState<View>('list');
  const [selectedProduct, setSelectedProduct] = useState<Product | null>(null);
  const { theme, toggleTheme } = useDarkMode();

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
        <button className="dark-mode-toggle sidebar-toggle" onClick={toggleTheme} title="Toggle dark mode">
          {theme === 'dark' ? '☀️' : '🌙'}
          <span>{theme === 'dark' ? 'Light Mode' : 'Dark Mode'}</span>
        </button>
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
