import React from 'react';

const Analytics = () => {
  const stats = [
    { title: 'Total Revenue', value: '$12,345', change: '+15%' },
    { title: 'Orders', value: '234', change: '+8%' },
    { title: 'Active Users', value: '1,234', change: '+12%' },
    { title: 'Average Cart Value', value: '$52.80', change: '+5%' },
  ];

  const recentTransactions = [
    { id: 1, user: 'John Doe', amount: '$49.99', date: '2024-02-20', status: 'Completed' },
    { id: 2, user: 'Jane Smith', amount: '$29.99', date: '2024-02-20', status: 'Completed' },
    { id: 3, user: 'Bob Johnson', amount: '$79.99', date: '2024-02-19', status: 'Pending' },
  ];

  const popularProducts = [
    { id: 1, name: 'Product 1', sales: 123, revenue: '$2,460' },
    { id: 2, name: 'Product 2', sales: 98, revenue: '$1,960' },
    { id: 3, name: 'Product 3', sales: 87, revenue: '$1,740' },
  ];

  return (
    <div className="container mx-auto px-4 py-8">
      <h1 className="text-3xl font-bold mb-8">Analytics Dashboard</h1>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
        {stats.map((stat, index) => (
          <div key={index} className="bg-white p-6 rounded-lg shadow">
            <h3 className="text-gray-500 text-sm">{stat.title}</h3>
            <p className="text-2xl font-semibold mt-2">{stat.value}</p>
            <span
              className={`text-sm ${
                stat.change.startsWith('+')
                  ? 'text-green-600'
                  : 'text-red-600'
              }`}
            >
              {stat.change} from last month
            </span>
          </div>
        ))}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        <div className="bg-white p-6 rounded-lg shadow">
          <h2 className="text-xl font-semibold mb-4">Recent Transactions</h2>
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead>
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    User
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Amount
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Date
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Status
                  </th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-200">
                {recentTransactions.map((transaction) => (
                  <tr key={transaction.id}>
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                      {transaction.user}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {transaction.amount}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {new Date(transaction.date).toLocaleDateString()}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span
                        className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${
                          transaction.status === 'Completed'
                            ? 'bg-green-100 text-green-800'
                            : 'bg-yellow-100 text-yellow-800'
                        }`}
                      >
                        {transaction.status}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        <div className="bg-white p-6 rounded-lg shadow">
          <h2 className="text-xl font-semibold mb-4">Popular Products</h2>
          <div className="space-y-4">
            {popularProducts.map((product) => (
              <div
                key={product.id}
                className="flex items-center justify-between p-4 bg-gray-50 rounded-lg"
              >
                <div>
                  <h3 className="font-medium">{product.name}</h3>
                  <p className="text-sm text-gray-500">
                    {product.sales} sales
                  </p>
                </div>
                <div className="text-right">
                  <p className="font-medium">{product.revenue}</p>
                  <p className="text-sm text-gray-500">Revenue</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      <div className="mt-8 bg-white p-6 rounded-lg shadow">
        <h2 className="text-xl font-semibold mb-4">Sales Chart</h2>
        <div className="h-64 bg-gray-100 rounded flex items-center justify-center">
          <p className="text-gray-500">Chart will be implemented here</p>
        </div>
      </div>
    </div>
  );
};

export default Analytics; 