import create from 'zustand';
import { persist } from 'zustand/middleware';
import { jwtDecode } from 'jwt-decode';
import axios from 'axios';
import toast from 'react-hot-toast';

const API_URL = process.env.REACT_APP_API_URL || 'http://192.168.74.207:5000';

// Sample admin credentials (replace with actual admin validation in production)
const ADMIN_CREDENTIALS = {
  email: 'admin@smartcart.com',
  password: 'admin123'
};

export const useAuthStore = create(
  persist(
    (set, get) => ({
      token: null,
      user: null,
      isAuthenticated: false,
      isLoading: false,
      error: null,
      
      setToken: (token) => {
        if (token) {
          const decoded = jwtDecode(token);
          set({ token, user: decoded, isAuthenticated: true });
        } else {
          set({ token: null, user: null, isAuthenticated: false });
        }
      },

      logout: () => {
        set({ token: null, user: null, isAuthenticated: false });
        toast.success('Logged out successfully');
      },

      refreshToken: async () => {
        try {
          const response = await fetch('/api/auth/refresh', {
            method: 'POST',
            headers: {
              'Authorization': `Bearer ${get().token}`
            }
          });
          
          if (response.ok) {
            const data = await response.json();
            const decoded = jwtDecode(data.token);
            set({ token: data.token, user: decoded, isAuthenticated: true });
            return true;
          }
          return false;
        } catch (error) {
          console.error('Error refreshing token:', error);
          return false;
        }
      },

      login: async (email, password, role = 'user') => {
        set({ isLoading: true, error: null });
        try {
          // Handle admin login
          if (role === 'admin') {
            if (email === ADMIN_CREDENTIALS.email && password === ADMIN_CREDENTIALS.password) {
              const adminUser = {
                email: ADMIN_CREDENTIALS.email,
                name: 'Admin',
                role: 'admin'
              };
              set({ 
                token: 'admin-token', // In production, use proper JWT
                user: adminUser,
                isAuthenticated: true,
                isLoading: false
              });
              return true;
            } else {
              throw new Error('Invalid admin credentials');
            }
          }

          // Handle regular user login
          const response = await axios.post(`${API_URL}/auth/login`, { email, password });
          const { token } = response.data;
          const decoded = jwtDecode(token);
          
          // Verify user role
          if (role === 'user' && decoded.role !== 'admin') {
            set({ token, user: decoded, isAuthenticated: true, isLoading: false });
            return true;
          } else {
            throw new Error('Invalid user credentials');
          }
        } catch (error) {
          const errorMessage = error.response?.data?.message || error.message || 'Login failed';
          set({ error: errorMessage, isLoading: false });
          toast.error(errorMessage);
          return false;
        }
      },

      register: async (userData) => {
        set({ isLoading: true, error: null });
        try {
          const response = await axios.post(`${API_URL}/auth/register`, userData);
          const { token } = response.data;
          set({ token, user: jwtDecode(token), isAuthenticated: true, isLoading: false });
          toast.success('Registration successful!');
          return true;
        } catch (error) {
          const errorMessage = error.response?.data?.message || 'Registration failed';
          set({ error: errorMessage, isLoading: false });
          toast.error(errorMessage);
          return false;
        }
      },

      updateProfile: async (userData) => {
        set({ isLoading: true, error: null });
        try {
          const response = await axios.put(
            `${API_URL}/user/profile`,
            userData,
            {
              headers: {
                Authorization: `Bearer ${get().token}`
              }
            }
          );
          const { user } = response.data;
          set({ user, isLoading: false });
          toast.success('Profile updated successfully!');
          return true;
        } catch (error) {
          const errorMessage = error.response?.data?.message || 'Profile update failed';
          set({ error: errorMessage, isLoading: false });
          toast.error(errorMessage);
          return false;
        }
      },

      clearError: () => set({ error: null })
    }),
    {
      name: 'auth-storage',
      getStorage: () => localStorage,
    }
  )
);

export default useAuthStore; 