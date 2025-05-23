import React from 'react';
import { useNavigate } from 'react-router-dom';

const AdminDashboard = () => {
  const navigate = useNavigate();

  const menuItems = [
    { title: 'Products', path: '/admin/products', icon: '📦' },
    { title: 'Stores', path: '/admin/stores', icon: '🏪' },
    { title: 'Cameras', path: '/admin/cameras', icon: '📸' },
    { title: 'Users', path: '/admin/users', icon: '👥' },
    { title: 'Analytics', path: '/admin/analytics', icon: '📊' },
  ];

  const stats = [
    { title: 'Total Products', value: '1,234' },
    { title: 'Active Stores', value: '12' },
    { title: 'Total Users', value: '5,678' },
    { title: 'Daily Orders', value: '89' },
  ];

  return (
    <div className="container mx-auto px-4 py-8">
      <h1 className="text-3xl font-bold mb-8">Admin Dashboard</h1>
      
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
        {stats.map((stat, index) => (
          <div key={index} className="bg-white p-6 rounded-lg shadow">
            <h3 className="text-gray-500 text-sm">{stat.title}</h3>
            <p className="text-2xl font-semibold mt-2">{stat.value}</p>
          </div>
        ))}
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-5 gap-4">
        {menuItems.map((item) => (
          <div
            key={item.path}
            className="bg-white p-6 rounded-lg shadow hover:shadow-lg cursor-pointer transition-shadow"
            onClick={() => navigate(item.path)}
          >
            <div className="text-4xl mb-4">{item.icon}</div>
            <h2 className="text-xl font-semibold">{item.title}</h2>
          </div>
        ))}
      </div>

      <div className="mt-8 grid grid-cols-1 lg:grid-cols-2 gap-8">
        <div className="bg-white p-6 rounded-lg shadow">
          <h2 className="text-xl font-semibold mb-4">Recent Activity</h2>
          <div className="space-y-4">
            {[1, 2, 3].map((i) => (
              <div key={i} className="flex items-center space-x-4">
                <div className="w-2 h-2 bg-blue-600 rounded-full"></div>
                <div>
                  <p className="text-gray-600">New order placed</p>
                  <p className="text-sm text-gray-500">2 minutes ago</p>
                </div>
              </div>
            ))}
          </div>
        </div>

        <div className="bg-white p-6 rounded-lg shadow">
          <h2 className="text-xl font-semibold mb-4">System Status</h2>
          <div className="space-y-4">
            <div className="flex justify-between items-center">
              <span>Server Status</span>
              <span className="px-2 py-1 bg-green-100 text-green-800 rounded-full text-sm">
                Operational
              </span>
            </div>
            <div className="flex justify-between items-center">
              <span>Database Status</span>
              <span className="px-2 py-1 bg-green-100 text-green-800 rounded-full text-sm">
                Healthy
              </span>
            </div>
            <div className="flex justify-between items-center">
              <span>API Status</span>
              <span className="px-2 py-1 bg-green-100 text-green-800 rounded-full text-sm">
                Online
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default AdminDashboard; 