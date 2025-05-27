import React, { useEffect, useState, useRef } from 'react';
import { io } from 'socket.io-client';
import { toast } from 'react-hot-toast';
import useCartStore from '../stores/cartStore';

const API_URL = process.env.REACT_APP_API_URL || 'http://192.168.74.207:5000';

const CameraFeed = ({ cartId }) => {
  const [isConnected, setIsConnected] = useState(false);
  const [lastDetection, setLastDetection] = useState(null);
  const socketRef = useRef(null);
  const imageRef = useRef(null);
  const addItem = useCartStore(state => state.addItem);

  useEffect(() => {
    // Connect to WebSocket server
    socketRef.current = io(API_URL, {
      transports: ['websocket'],
      upgrade: false,
      reconnection: true,
      reconnectionAttempts: 5,
      reconnectionDelay: 1000,
      reconnectionDelayMax: 5000,
      timeout: 60000,
      path: '/socket.io',
      query: { cart_id: cartId }
    });

    // Handle connection events
    socketRef.current.on('connect', () => {
      console.log('Connected to server');
      setIsConnected(true);
      toast.success('Connected to camera feed');
    });

    socketRef.current.on('connect_error', (error) => {
      console.error('Connection error:', error);
      toast.error(`Connection error: ${error.message}`);
    });

    socketRef.current.on('disconnect', () => {
      console.log('Disconnected from server');
      setIsConnected(false);
      toast.error('Camera feed disconnected');
    });

    socketRef.current.on('connection_success', (data) => {
      console.log('Connection success:', data);
    });

    // Handle incoming frames
    socketRef.current.on('esp32_frame', (data) => {
      console.log('Received frame');
      if (imageRef.current && data.image) {
        imageRef.current.src = `data:image/jpeg;base64,${data.image}`;
      }
    });

    // Handle product detections
    socketRef.current.on('detection_result', (data) => {
      console.log('Detection result:', data);
      if (data.cart_id === cartId) {
        setLastDetection(data);

        // Add detected product to cart
        const product = {
          id: data.class,
          name: data.class,
          price: 0,
          confidence: data.confidence
        };

        addItem(product);
        toast.success(`Detected: ${product.name}`);
      }
    });

    socketRef.current.on('error', (error) => {
      console.error('Server error:', error);
      toast.error(`Server error: ${error.message}`);
    });

    return () => {
      if (socketRef.current) {
        socketRef.current.disconnect();
      }
    };
  }, [cartId, addItem]);

  // --- Fetch latest image from backend every 5 seconds ---
  useEffect(() => {
    const fetchImage = () => {
      fetch(`${API_URL}/latest_image`)
        .then(res => {
          if (!res.ok) throw new Error('No image');
          return res.blob();
        })
        .then(blob => {
          if (imageRef.current) {
            imageRef.current.src = URL.createObjectURL(blob);
          }
        })
        .catch(() => {
          if (imageRef.current) imageRef.current.src = '';
        });
    };
    fetchImage();
    const interval = setInterval(fetchImage, 5000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="bg-white p-4 rounded-lg shadow">
      <div className="mb-4">
        <h2 className="text-xl font-semibold mb-2">Camera Feed</h2>
        <div className="flex items-center space-x-2">
          <div
            className={`w-3 h-3 rounded-full ${
              isConnected ? 'bg-green-500' : 'bg-red-500'
            }`}
          />
          <span className="text-sm text-gray-600">
            {isConnected ? 'Connected' : 'Disconnected'}
          </span>
        </div>
      </div>

      <div className="relative aspect-video bg-gray-100 rounded-lg overflow-hidden mb-4">
        <img
          ref={imageRef}
          alt="Camera feed"
          className="w-full h-full object-cover"
        />
        {!isConnected && (
          <div className="absolute inset-0 flex items-center justify-center bg-gray-900 bg-opacity-50 text-white">
            Connecting to camera...
          </div>
        )}
      </div>

      {lastDetection && (
        <div className="p-3 bg-blue-50 rounded-lg">
          <h3 className="font-medium mb-1">Last Detection</h3>
          <div className="text-sm text-gray-600">
            <p>Product: {lastDetection.class}</p>
            <p>
              Confidence: {(lastDetection.confidence * 100).toFixed(1)}%
            </p>
          </div>
        </div>
      )}
    </div>
  );
};

export default CameraFeed;