import React, { useEffect, useState } from 'react';
import useCartStore from '../../stores/cartStore';
import { toast } from 'react-hot-toast';
import CameraFeed from '../../components/CameraFeed';

const CameraTab = () => {
  const [cartId] = useState(() => 'cart_' + Math.random().toString(36).substr(2, 9));
  const addItem = useCartStore((state) => state.addItem);
  const [isConnected, setIsConnected] = useState(false);

  const handleProductDetected = (detection) => {
    if (detection && detection.product_id) {
      // Fetch product details from your inventory
      const product = {
        id: detection.product_id,
        name: detection.product_id, // You should map this to actual product name
        price: 9.99, // This should come from your product database
        quantity: 1
      };
      
      addItem(product);
      toast.success(`Added ${product.name} to cart!`);
    }
  };

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="bg-white rounded-lg shadow-lg p-6">
        <h2 className="text-2xl font-bold mb-4">Smart Camera Detection</h2>
        <div className="mb-4">
          <p className="text-gray-600">
            Point the camera at a product to automatically add it to your cart.
          </p>
        </div>
        
        <div className="aspect-video bg-gray-100 rounded-lg overflow-hidden">
          <CameraFeed 
            cartId={cartId}
            onProductDetected={handleProductDetected}
            onConnectionChange={setIsConnected}
          />
        </div>

        <div className="mt-4">
          <div className="flex items-center space-x-2">
            <div className={`w-3 h-3 rounded-full ${isConnected ? 'bg-green-500' : 'bg-red-500'}`} />
            <span className="text-sm text-gray-600">
              {isConnected ? 'Camera Connected' : 'Camera Disconnected'}
            </span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default CameraTab; 