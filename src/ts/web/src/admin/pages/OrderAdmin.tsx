import React, { useState } from 'react';
import { useQuery, useMutation } from '@apollo/client';
import { Order, OrderState } from '../../shared/types';
import { GET_ORDERS, SHIP_ORDER, COMPLETE_ORDER, CANCEL_ORDER } from '../queries';
import {
  GetOrdersQuery,
  GetOrdersQueryVariables,
  ShipOrderMutation,
  ShipOrderMutationVariables,
  CompleteOrderMutation,
  CompleteOrderMutationVariables,
  CancelOrderMutation,
  CancelOrderMutationVariables,
} from '../../generated/graphql';
import './OrderAdmin.css';

const OrderAdmin: React.FC = () => {
  const [pageSize, setPageSize] = useState(10);
  const [currentPage, setCurrentPage] = useState(1);
  const [menuOpen, setMenuOpen] = useState<string | null>(null);

  const { data, loading, refetch } = useQuery<GetOrdersQuery, GetOrdersQueryVariables>(
    GET_ORDERS,
    {
      variables: { first: 1000 },
    }
  );

  const [shipOrder] = useMutation<ShipOrderMutation, ShipOrderMutationVariables>(SHIP_ORDER);
  const [completeOrder] = useMutation<CompleteOrderMutation, CompleteOrderMutationVariables>(
    COMPLETE_ORDER
  );
  const [cancelOrder] = useMutation<CancelOrderMutation, CancelOrderMutationVariables>(
    CANCEL_ORDER
  );

  const orders = data?.orders.edges.map(edge => edge.node) || [];
  const totalPages = Math.ceil(orders.length / pageSize);
  const startIndex = (currentPage - 1) * pageSize;
  const endIndex = startIndex + pageSize;
  const currentOrders = orders.slice(startIndex, endIndex);

  const toggleMenu = (orderId: string) => {
    setMenuOpen(menuOpen === orderId ? null : orderId);
  };

  const formatDate = (dateString: string) => {
    return new Intl.DateTimeFormat('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    }).format(new Date(dateString));
  };

  const handleUpdateOrderState = async (
    orderId: string,
    action: 'ship' | 'complete' | 'cancel'
  ) => {
    try {
      if (action === 'ship') {
        await shipOrder({ variables: { id: orderId } });
      } else if (action === 'complete') {
        await completeOrder({ variables: { id: orderId } });
      } else if (action === 'cancel') {
        await cancelOrder({ variables: { id: orderId } });
      }
      await refetch();
      setMenuOpen(null);
    } catch (error) {
      console.error('Error updating order state:', error);
    }
  };

  const canShip = (state: OrderState) => state === 'PROCESSING';
  const canComplete = (state: OrderState) => state === 'SHIPPED';
  const canCancel = (state: OrderState) => state === 'PROCESSING' || state === 'SHIPPED';

  return (
    <div className="order-admin">
      <div className="page-header">
        <h1>Order Management</h1>
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

      <div className="order-table">
        <div className="table-header">
          <div className="col-id">Order ID</div>
          <div className="col-date">Date & Time</div>
          <div className="col-state">State</div>
          <div className="col-price">Total Price</div>
          <div className="col-customer">Customer Name</div>
          <div className="col-email">Email</div>
          <div className="col-actions">Actions</div>
        </div>

        {currentOrders.map(order => (
          <div key={order.id} className="table-row">
            <div className="col-id">{order.id}</div>
            <div className="col-date">{formatDate(order.createdAt)}</div>
            <div className="col-state">
              <span className={`state-badge ${order.state.toLowerCase()}`}>
                {order.state.charAt(0) + order.state.slice(1).toLowerCase()}
              </span>
            </div>
            <div className="col-price">${(order.totalPrice / 100).toFixed(2)}</div>
            <div className="col-customer">{order.customerName}</div>
            <div className="col-email">{order.customerEmail}</div>
            <div className="col-actions">
              <button
                className="action-button"
                onClick={() => toggleMenu(order.id)}
              >
                ⋮
              </button>
              {menuOpen === order.id && (
                <div className="action-menu">
                  {canShip(order.state) && (
                    <button onClick={() => handleUpdateOrderState(order.id, 'ship')}>
                      Ship
                    </button>
                  )}
                  {canComplete(order.state) && (
                    <button onClick={() => handleUpdateOrderState(order.id, 'complete')}>
                      Complete
                    </button>
                  )}
                  {canCancel(order.state) && (
                    <button onClick={() => handleUpdateOrderState(order.id, 'cancel')}>
                      Cancel
                    </button>
                  )}
                </div>
              )}
            </div>
          </div>
        ))}
      </div>

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

export default OrderAdmin;
