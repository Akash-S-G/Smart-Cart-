import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import useCartStore from '../stores/cartStore';

const Navigation = () => {
  const location = useLocation();
  const items = useCartStore((state) => state.items);
  const cartItemCount = items.reduce((total, item) => total + item.quantity, 0);

  const isActive = (path) => location.pathname === path;

  return (
    <nav className="bg-white shadow-lg">
      <div className="container mx-auto px-4">
        <div className="flex justify-between items-center h-16">
          <div className="flex items-center">
            <Link to="/" className="text-xl font-bold text-gray-800">
              SmartCart
            </Link>
          </div>

          <div className="flex items-center space-x-4">
            <Link
              to="/camera"
              className={`px-3 py-2 rounded-md text-sm font-medium ${
                isActive('/camera')
                  ? 'bg-blue-500 text-white'
                  : 'text-gray-600 hover:bg-gray-100'
              }`}
            >
              Camera
            </Link>
            
            <Link
              to="/cart"
              className={`px-3 py-2 rounded-md text-sm font-medium relative ${
                isActive('/cart')
                  ? 'bg-blue-500 text-white'
                  : 'text-gray-600 hover:bg-gray-100'
              }`}
            >
              Cart
              {cartItemCount > 0 && (
                <span className="absolute -top-1 -right-1 bg-red-500 text-white text-xs rounded-full h-5 w-5 flex items-center justify-center">
                  {cartItemCount}
                </span>
              )}
            </Link>
          </div>
        </div>
      </div>
    </nav>
  );
};

export default Navigation; 