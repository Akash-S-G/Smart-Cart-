import React, { useState } from 'react';

const StoreManagement = () => {
  const [stores] = useState([
    {
      id: 1,
      name: 'Smart Store Downtown',
      address: '123 Main St, Downtown',
      manager: 'John Doe',
      status: 'Active',
      cameras: 4,
    },
    {
      id: 2,
      name: 'Smart Store Uptown',
      address: '456 Park Ave, Uptown',
      manager: 'Jane Smith',
      status: 'Active',
      cameras: 3,
    },
    {
      id: 3,
      name: 'Smart Store West',
      address: '789 West St, Westside',
      manager: 'Bob Johnson',
      status: 'Maintenance',
      cameras: 2,
    },
  ]);

  const [searchTerm, setSearchTerm] = useState('');

  const filteredStores = stores.filter((store) =>
    store.name.toLowerCase().includes(searchTerm.toLowerCase())
  );

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-3xl font-bold">Store Management</h1>
        <button className="bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700">
          Add New Store
        </button>
      </div>

      <div className="mb-6">
        <input
          type="text"
          placeholder="Search stores..."
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          className="w-full md:w-1/3 px-4 py-2 rounded-md border border-gray-300 focus:outline-none focus:ring-2 focus:ring-blue-500"
        />
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {filteredStores.map((store) => (
          <div key={store.id} className="bg-white rounded-lg shadow p-6">
            <div className="flex justify-between items-start mb-4">
              <div>
                <h2 className="text-xl font-semibold">{store.name}</h2>
                <p className="text-gray-600 text-sm mt-1">{store.address}</p>
              </div>
              <span
                className={`px-2 py-1 rounded-full text-xs font-semibold ${
                  store.status === 'Active'
                    ? 'bg-green-100 text-green-800'
                    : 'bg-yellow-100 text-yellow-800'
                }`}
              >
                {store.status}
              </span>
            </div>
            <div className="space-y-2 text-sm text-gray-600">
              <div className="flex justify-between">
                <span>Store Manager:</span>
                <span className="font-medium text-gray-900">{store.manager}</span>
              </div>
              <div className="flex justify-between">
                <span>Active Cameras:</span>
                <span className="font-medium text-gray-900">{store.cameras}</span>
              </div>
            </div>
            <div className="mt-6 flex space-x-3">
              <button className="flex-1 bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700">
                Edit
              </button>
              <button className="flex-1 bg-gray-100 text-gray-700 px-4 py-2 rounded-md hover:bg-gray-200">
                View Details
              </button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default StoreManagement; 