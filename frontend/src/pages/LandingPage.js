import React from 'react';
import { Link } from 'react-router-dom';
import { useAuthStore } from '../stores/authStore';

const LandingPage = () => {
  const isAuthenticated = useAuthStore(state => state.isAuthenticated);

  const features = [
    {
      title: 'Smart Shopping',
      description: 'AI-powered cart that automatically detects and tracks your items',
      icon: '🛒',
      path: isAuthenticated ? '/cart' : '/register',
    },
    {
      title: 'Real-time Updates',
      description: 'Get instant updates on your cart and shopping progress',
      icon: '⚡',
      path: isAuthenticated ? '/dashboard' : '/register',
    },
    {
      title: 'Store Locator',
      description: 'Find the nearest smart stores in your area',
      icon: '📍',
      path: isAuthenticated ? '/stores' : '/register',
    },
    {
      title: 'Easy Checkout',
      description: 'Seamless and quick checkout process',
      icon: '✨',
      path: isAuthenticated ? '/cart' : '/register',
    },
  ];

  return (
    <div className="container mx-auto px-4 py-12">
      <div className="text-center mb-16">
        <h1 className="text-4xl md:text-6xl font-bold mb-6">
          Welcome to Smart Cart AI
        </h1>
        <p className="text-xl text-gray-600 mb-8">
          Experience the future of shopping with our AI-powered cart system
        </p>
        <div className="flex justify-center space-x-4">
          <Link
            to={isAuthenticated ? '/dashboard' : '/register'}
            className="bg-blue-600 text-white px-8 py-3 rounded-md hover:bg-blue-700"
          >
            {isAuthenticated ? 'Go to Dashboard' : 'Get Started'}
          </Link>
          <Link
            to="/about"
            className="bg-gray-100 text-gray-700 px-8 py-3 rounded-md hover:bg-gray-200"
          >
            Learn More
          </Link>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8 mb-16">
        {features.map((feature, index) => (
          <Link
            key={index}
            to={feature.path}
            className="bg-white p-6 rounded-lg shadow-md hover:shadow-lg transition-all hover:bg-gray-50 cursor-pointer"
          >
            <div className="text-4xl mb-4">{feature.icon}</div>
            <h3 className="text-xl font-semibold mb-2">{feature.title}</h3>
            <p className="text-gray-600">{feature.description}</p>
          </Link>
        ))}
      </div>

      <div className="bg-gray-50 rounded-lg p-8 text-center">
        <h2 className="text-3xl font-bold mb-4">Ready to Transform Your Shopping?</h2>
        <p className="text-gray-600 mb-6">
          Join thousands of happy customers who have switched to Smart Cart AI
        </p>
        <Link
          to={isAuthenticated ? '/dashboard' : '/register'}
          className="bg-blue-600 text-white px-8 py-3 rounded-md hover:bg-blue-700 inline-block"
        >
          {isAuthenticated ? 'Go to Dashboard' : 'Sign Up Now'}
        </Link>
      </div>
    </div>
  );
};

export default LandingPage; 