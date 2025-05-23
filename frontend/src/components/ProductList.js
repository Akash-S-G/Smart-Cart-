import React from 'react';
import useCartStore from '../stores/cartStore';
import { toast } from 'react-hot-toast';

// Sample products data (replace with actual API call)
const products = [
  { id: 1, name: 'Product 1', price: 19.99, description: 'Description for product 1' },
  { id: 2, name: 'Product 2', price: 29.99, description: 'Description for product 2' },
  { id: 3, name: 'Product 3', price: 39.99, description: 'Description for product 3' },
  { id: 4, name: 'Product 4', price: 49.99, description: 'Description for product 4' },
];

const ProductList = () => {
  const addItem = useCartStore(state => state.addItem);

  const handleAddToCart = (product) => {
    addItem(product);
    toast.success(`${product.name} added to cart`);
  };

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
      {products.map((product) => (
        <div key={product.id} className="bg-white rounded-lg shadow p-6">
          <div className="h-40 bg-gray-200 rounded-lg mb-4"></div>
          <h3 className="text-lg font-semibold mb-2">{product.name}</h3>
          <p className="text-gray-600 mb-4">{product.description}</p>
          <div className="flex items-center justify-between">
            <span className="text-lg font-bold">${product.price.toFixed(2)}</span>
            <button
              onClick={() => handleAddToCart(product)}
              className="bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700"
            >
              Add to Cart
            </button>
          </div>
        </div>
      ))}
    </div>
  );
};

export default ProductList; 