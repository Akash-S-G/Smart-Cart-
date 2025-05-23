import React from 'react';
import { Link } from 'react-router-dom';
import { useAuthStore } from '../../stores/authStore';
import ProductList from '../../components/ProductList';

const Dashboard = () => {
  const user = useAuthStore((state) => state.user);

  const cards = [
    {
      title: 'My Cart',
      description: 'View and manage your shopping cart',
      path: '/cart',
      icon: '🛒',
    },
    {
      title: 'Order History',
      description: 'Track your past orders',
      path: '/orders',
      icon: '📦',
    },
    {
      title: 'Find Stores',
      description: 'Locate Smart Cart enabled stores',
      path: '/stores',
      icon: '🏪',
    },
    {
      title: 'Profile Settings',
      description: 'Update your account information',
      path: '/profile',
      icon: '👤',
    },
  ];

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold mb-2">Welcome, {user?.name || 'Guest'}!</h1>
        <p className="text-gray-600">Browse our products and add them to your cart.</p>
      </div>
      
      <div className="mb-8">
        <h2 className="text-2xl font-semibold mb-4">Available Products</h2>
        <ProductList />
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {cards.map((card, index) => (
          <Link
            key={index}
            to={card.path}
            className="bg-white p-6 rounded-lg shadow-md hover:shadow-lg transition-shadow"
          >
            <div className="text-4xl mb-4">{card.icon}</div>
            <h2 className="text-xl font-semibold mb-2">{card.title}</h2>
            <p className="text-gray-600">{card.description}</p>
          </Link>
        ))}
      </div>

      <div className="mt-12 grid grid-cols-1 lg:grid-cols-2 gap-8">
        <div className="bg-white p-6 rounded-lg shadow-md">
          <h2 className="text-xl font-semibold mb-4">Recent Orders</h2>
          <div className="space-y-4">
            <p className="text-gray-600">No recent orders found.</p>
          </div>
        </div>

        <div className="bg-white p-6 rounded-lg shadow-md">
          <h2 className="text-xl font-semibold mb-4">Nearby Stores</h2>
          <div className="space-y-4">
            <p className="text-gray-600">Loading stores...</p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard; 