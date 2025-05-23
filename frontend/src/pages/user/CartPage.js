import React from 'react';
import useCartStore from '../../stores/cartStore';
import { toast } from 'react-hot-toast';

const CartPage = () => {
  const { items, removeItem, updateQuantity, getTotal } = useCartStore();

  const handleUpdateQuantity = (productId, currentQuantity, change) => {
    const newQuantity = currentQuantity + change;
    if (newQuantity <= 0) {
      handleRemoveItem(productId);
    } else {
      updateQuantity(productId, newQuantity);
    }
  };

  const handleRemoveItem = (productId) => {
    removeItem(productId);
    toast.success('Item removed from cart');
  };

  const handleCheckout = () => {
    toast.success('Proceeding to checkout...');
    // Add checkout logic here
  };

  return (
    <div className="container mx-auto px-4 py-8">
      <h1 className="text-3xl font-bold mb-6">Shopping Cart</h1>
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        <div className="lg:col-span-2">
          {items.length === 0 ? (
            <div className="text-center py-8">
              <p className="text-gray-500">Your cart is empty</p>
            </div>
          ) : (
            <div className="space-y-4">
              {items.map((item) => (
                <div
                  key={item.id}
                  className="flex items-center justify-between p-4 bg-white rounded-lg shadow"
                >
                  <div>
                    <h3 className="font-semibold">{item.name}</h3>
                    <p className="text-gray-600">${item.price.toFixed(2)}</p>
                  </div>
                  <div className="flex items-center space-x-4">
                    <div className="flex items-center space-x-2">
                      <button 
                        className="p-1 rounded-md hover:bg-gray-100"
                        onClick={() => handleUpdateQuantity(item.id, item.quantity, -1)}
                      >
                        -
                      </button>
                      <span>{item.quantity}</span>
                      <button 
                        className="p-1 rounded-md hover:bg-gray-100"
                        onClick={() => handleUpdateQuantity(item.id, item.quantity, 1)}
                      >
                        +
                      </button>
                    </div>
                    <button 
                      className="text-red-500 hover:text-red-700"
                      onClick={() => handleRemoveItem(item.id)}
                    >
                      Remove
                    </button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
        <div className="bg-white p-6 rounded-lg shadow h-fit">
          <h2 className="text-xl font-semibold mb-4">Order Summary</h2>
          <div className="space-y-2 mb-4">
            <div className="flex justify-between">
              <span>Subtotal</span>
              <span>${getTotal().toFixed(2)}</span>
            </div>
            <div className="flex justify-between">
              <span>Shipping</span>
              <span>Free</span>
            </div>
            <div className="border-t pt-2 mt-2">
              <div className="flex justify-between font-semibold">
                <span>Total</span>
                <span>${getTotal().toFixed(2)}</span>
              </div>
            </div>
          </div>
          <button 
            className="w-full bg-blue-600 text-white py-2 px-4 rounded-md hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
            onClick={handleCheckout}
            disabled={items.length === 0}
          >
            Proceed to Checkout
          </button>
        </div>
      </div>
    </div>
  );
};

export default CartPage; 