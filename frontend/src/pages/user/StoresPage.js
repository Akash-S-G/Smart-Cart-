import React, { useState } from 'react';

const StoresPage = () => {
  const [stores] = useState([
    {
      id: 1,
      name: 'Smart Store Downtown',
      address: '123 Main St, Downtown',
      distance: '0.5 miles',
      status: 'Open',
    },
    {
      id: 2,
      name: 'Smart Store Uptown',
      address: '456 Park Ave, Uptown',
      distance: '1.2 miles',
      status: 'Open',
    },
    {
      id: 3,
      name: 'Smart Store West',
      address: '789 West St, Westside',
      distance: '2.0 miles',
      status: 'Closed',
    },
  ]);

  return (
    <div className="container mx-auto px-4 py-8">
      <h1 className="text-3xl font-bold mb-6">Nearby Stores</h1>
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        <div className="space-y-4">
          {stores.map((store) => (
            <div
              key={store.id}
              className="bg-white p-6 rounded-lg shadow hover:shadow-md transition-shadow"
            >
              <div className="flex justify-between items-start">
                <div>
                  <h2 className="text-xl font-semibold mb-2">{store.name}</h2>
                  <p className="text-gray-600 mb-1">{store.address}</p>
                  <p className="text-gray-500">{store.distance}</p>
                </div>
                <span
                  className={`px-3 py-1 rounded-full text-sm ${
                    store.status === 'Open'
                      ? 'bg-green-100 text-green-800'
                      : 'bg-red-100 text-red-800'
                  }`}
                >
                  {store.status}
                </span>
              </div>
              <div className="mt-4 flex space-x-4">
                <button className="bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700">
                  View Store
                </button>
                <button className="bg-gray-100 text-gray-700 px-4 py-2 rounded-md hover:bg-gray-200">
                  Get Directions
                </button>
              </div>
            </div>
          ))}
        </div>
        <div className="bg-gray-200 rounded-lg h-[500px] flex items-center justify-center">
          <p className="text-gray-500">Map integration will be added here</p>
        </div>
      </div>
    </div>
  );
};

export default StoresPage; 