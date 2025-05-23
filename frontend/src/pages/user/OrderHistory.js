import React, { useState } from 'react';

const OrderHistory = () => {
  const [orders] = useState([
    {
      id: 1,
      date: '2024-02-20',
      status: 'Delivered',
      total: 49.98,
      items: [
        { id: 1, name: 'Product 1', quantity: 2, price: 19.99 },
        { id: 2, name: 'Product 2', quantity: 1, price: 29.99 },
      ],
    },
    {
      id: 2,
      date: '2024-02-18',
      status: 'Processing',
      total: 89.97,
      items: [
        { id: 3, name: 'Product 3', quantity: 3, price: 29.99 },
      ],
    },
  ]);

  const getStatusColor = (status) => {
    switch (status) {
      case 'Delivered':
        return 'bg-green-100 text-green-800';
      case 'Processing':
        return 'bg-yellow-100 text-yellow-800';
      case 'Cancelled':
        return 'bg-red-100 text-red-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  return (
    <div className="container mx-auto px-4 py-8">
      <h1 className="text-3xl font-bold mb-6">Order History</h1>
      <div className="space-y-6">
        {orders.map((order) => (
          <div key={order.id} className="bg-white rounded-lg shadow p-6">
            <div className="flex justify-between items-start mb-4">
              <div>
                <p className="text-sm text-gray-500">Order #{order.id}</p>
                <p className="text-sm text-gray-500">
                  Placed on {new Date(order.date).toLocaleDateString()}
                </p>
              </div>
              <span
                className={`px-3 py-1 rounded-full text-sm ${getStatusColor(
                  order.status
                )}`}
              >
                {order.status}
              </span>
            </div>
            <div className="border-t border-b py-4 my-4">
              {order.items.map((item) => (
                <div
                  key={item.id}
                  className="flex justify-between items-center py-2"
                >
                  <div>
                    <p className="font-medium">{item.name}</p>
                    <p className="text-sm text-gray-500">
                      Quantity: {item.quantity}
                    </p>
                  </div>
                  <p className="text-gray-600">
                    ${(item.price * item.quantity).toFixed(2)}
                  </p>
                </div>
              ))}
            </div>
            <div className="flex justify-between items-center">
              <p className="font-semibold">Total</p>
              <p className="font-semibold">${order.total.toFixed(2)}</p>
            </div>
            <div className="mt-4 flex space-x-4">
              <button className="bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700">
                View Details
              </button>
              <button className="bg-gray-100 text-gray-700 px-4 py-2 rounded-md hover:bg-gray-200">
                Track Order
              </button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default OrderHistory; 