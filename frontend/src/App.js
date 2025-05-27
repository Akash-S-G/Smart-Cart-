import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { Toaster } from 'react-hot-toast';
import { useAuthStore } from './stores/authStore';
import Layout from './components/Layout';
import ProtectedRoute from './components/ProtectedRoute';
import AdminRoute from './components/AdminRoute';

// Public Pages
import LandingPage from './pages/LandingPage';
import LoginPage from './pages/LoginPage';
import RegisterPage from './pages/RegisterPage';
import AboutPage from './pages/AboutPage';
import ContactPage from './pages/ContactPage';

// User Pages
import Dashboard from './pages/user/Dashboard';
import CartPage from './pages/user/CartPage';
import StoresPage from './pages/user/StoresPage';
import ProfilePage from './pages/user/ProfilePage';
import OrderHistory from './pages/user/OrderHistory';
import CameraTab from './pages/user/CameraTab';

// Admin Pages
import AdminDashboard from './pages/admin/Dashboard';
import ProductManagement from './pages/admin/ProductManagement';
import StoreManagement from './pages/admin/StoreManagement';
import CameraManagement from './pages/admin/CameraManagement';
import UserManagement from './pages/admin/UserManagement';
import Analytics from './pages/admin/Analytics';

// import Product from './Product';
function App() {
  const isAuthenticated = useAuthStore(state => state.isAuthenticated);
  const user = useAuthStore(state => state.user);

  return (
    <Router>
      <div className="min-h-screen bg-gray-100">
        <Toaster position="top-right" />
        <main>
          <Routes>
            {/* Public Routes */}
            <Route path="/" element={<Layout><LandingPage /></Layout>} />
            <Route path="/about" element={<Layout><AboutPage /></Layout>} />
            <Route path="/contact" element={<Layout><ContactPage /></Layout>} />
            <Route 
              path="/login" 
              element={
                !isAuthenticated ? (
                  <Layout><LoginPage /></Layout>
                ) : (
                  <Navigate to={user?.role === 'admin' ? '/admin/dashboard' : '/dashboard'} />
                )
              } 
            />
            <Route 
              path="/register" 
              element={
                !isAuthenticated ? (
                  <Layout><RegisterPage /></Layout>
                ) : (
                  <Navigate to="/dashboard" />
                )
              } 
            />

            {/* User Routes */}
            <Route path="/dashboard" element={<ProtectedRoute><Layout><Dashboard /></Layout></ProtectedRoute>} />
            <Route path="/cart" element={<ProtectedRoute><Layout><CartPage /></Layout></ProtectedRoute>} />
            <Route path="/stores" element={<ProtectedRoute><Layout><StoresPage /></Layout></ProtectedRoute>} />
            <Route path="/profile" element={<ProtectedRoute><Layout><ProfilePage /></Layout></ProtectedRoute>} />
            <Route path="/orders" element={<ProtectedRoute><Layout><OrderHistory /></Layout></ProtectedRoute>} />
            <Route path="/camera" element={<Layout><CameraTab /></Layout>} />

            {/* Admin Routes */}
            <Route path="/admin/dashboard" element={<AdminRoute><Layout><AdminDashboard /></Layout></AdminRoute>} />
            <Route path="/admin/products" element={<AdminRoute><Layout><ProductManagement /></Layout></AdminRoute>} />
            <Route path="/admin/stores" element={<AdminRoute><Layout><StoreManagement /></Layout></AdminRoute>} />
            <Route path="/admin/cameras" element={<AdminRoute><Layout><CameraManagement /></Layout></AdminRoute>} />
            <Route path="/admin/users" element={<AdminRoute><Layout><UserManagement /></Layout></AdminRoute>} />
            <Route path="/admin/analytics" element={<AdminRoute><Layout><Analytics /></Layout></AdminRoute>} />
          
          </Routes>
        </main>
      </div>
    </Router>
  );
}

export default App; 