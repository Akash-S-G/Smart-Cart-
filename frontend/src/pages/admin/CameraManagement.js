import React, { useState } from 'react';

const CameraManagement = () => {
  const [cameras] = useState([
    {
      id: 1,
      name: 'Camera 1',
      store: 'Smart Store Downtown',
      location: 'Entrance',
      status: 'Online',
      lastSeen: '2024-02-20T15:30:00',
    },
    {
      id: 2,
      name: 'Camera 2',
      store: 'Smart Store Downtown',
      location: 'Aisle 1',
      status: 'Online',
      lastSeen: '2024-02-20T15:29:00',
    },
    {
      id: 3,
      name: 'Camera 3',
      store: 'Smart Store Uptown',
      location: 'Checkout',
      status: 'Offline',
      lastSeen: '2024-02-20T14:45:00',
    },
  ]);

  const [selectedStore, setSelectedStore] = useState('All');
  const stores = ['All', 'Smart Store Downtown', 'Smart Store Uptown'];

  const filteredCameras = cameras.filter(
    (camera) => selectedStore === 'All' || camera.store === selectedStore
  );

  const getStatusColor = (status) => {
    return status === 'Online'
      ? 'bg-green-100 text-green-800'
      : 'bg-red-100 text-red-800';
  };

  const formatLastSeen = (dateString) => {
    const date = new Date(dateString);
    return date.toLocaleString();
  };

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-3xl font-bold">Camera Management</h1>
        <button className="bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700">
          Add New Camera
        </button>
      </div>

      <div className="mb-6">
        <select
          value={selectedStore}
          onChange={(e) => setSelectedStore(e.target.value)}
          className="px-4 py-2 rounded-md border border-gray-300 focus:outline-none focus:ring-2 focus:ring-blue-500"
        >
          {stores.map((store) => (
            <option key={store} value={store}>
              {store}
            </option>
          ))}
        </select>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {filteredCameras.map((camera) => (
          <div key={camera.id} className="bg-white rounded-lg shadow p-6">
            <div className="flex justify-between items-start mb-4">
              <div>
                <h2 className="text-xl font-semibold">{camera.name}</h2>
                <p className="text-gray-600 text-sm mt-1">{camera.store}</p>
                <p className="text-gray-500 text-sm">{camera.location}</p>
              </div>
              <span
                className={`px-2 py-1 rounded-full text-xs font-semibold ${getStatusColor(
                  camera.status
                )}`}
              >
                {camera.status}
              </span>
            </div>
            <div className="text-sm text-gray-500">
              Last seen: {formatLastSeen(camera.lastSeen)}
            </div>
            <div className="mt-6 flex space-x-3">
              <button className="flex-1 bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700">
                View Stream
              </button>
              <button className="flex-1 bg-gray-100 text-gray-700 px-4 py-2 rounded-md hover:bg-gray-200">
                Settings
              </button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default CameraManagement; 