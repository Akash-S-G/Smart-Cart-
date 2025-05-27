import React, { useEffect, useState, useRef } from 'react';
import { io } from 'socket.io-client';
import { toast } from 'react-hot-toast';
import useCartStore from '../stores/cartStore';

const API_URL = process.env.REACT_APP_API_URL || 'http://192.168.74.207:5000';

const CameraFeed = ({ cartId }) => {
  const [isConnected, setIsConnected] = useState(false);
  const [lastDetection, setLastDetection] = useState(0);
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

  // --- Fetch latest image from backend every 1 second ---
  useEffect(() => {
    let lastImageUrl = null;
    const fetchImage = () => {
      fetch(`${API_URL}/latest_image?_t=${Date.now()}`)
        .then(res => {
          if (!res.ok) throw new Error('No image');
          return res.blob();
        })
        .then(blob => {
          if (imageRef.current) {
            // Revoke previous object URL to avoid memory leak
            if (lastImageUrl) URL.revokeObjectURL(lastImageUrl);
            lastImageUrl = URL.createObjectURL(blob);
            imageRef.current.src = lastImageUrl;
          }
        })
        .catch(() => {
          if (imageRef.current) imageRef.current.src = '';
        });
    };
    fetchImage();
    const interval = setInterval(fetchImage, 500); // 0.5 second for faster updates
    return () => {
      clearInterval(interval);
      if (lastImageUrl) URL.revokeObjectURL(lastImageUrl);
    };
  }, []);

  // --- Fetch latest prediction from backend every 1 second ---
  useEffect(() => {
    const fetchPrediction = () => {
      fetch(`${API_URL}/latest_prediction`)
        .then(res => res.json())
        .then(data => {
          console.log('[CameraFeed] /latest_prediction response:', data); // Debug log
          if (data && typeof data.confidence !== 'undefined' && data.product_name) {
            setLastDetection(data);
            // Only add to cart if product is recognized and confidence >= 0.85
            if (
              data.product_name !== 'Unknown or Not Recognized' &&
              typeof data.confidence === 'number' &&
              data.confidence >= 0.85
            ) {
              const price = Math.floor(Math.random() * 100) + 1; // random price 1-100
              addItem({
                id: data.product_id,
                name: data.product_name,
                price,
                confidence: data.confidence
              });
              toast.success(`Added to cart: ${data.product_name} (₹${price})`);
            }
          }
        })
        .catch(() => { });
    };
    fetchPrediction();
    const interval = setInterval(fetchPrediction, 1000); // 1 second
    return () => clearInterval(interval);
  }, [cartId, addItem]);

  return (
    <div className="bg-white p-4 rounded-lg shadow">
      <div className="mb-4">
        <h2 className="text-xl font-semibold mb-2">Camera Feed</h2>
        <div className="flex items-center space-x-2">
          <div
            className={`w-3 h-3 rounded-full ${isConnected ? 'bg-green-500' : 'bg-red-500'}`}
          />
          <span className="text-sm text-gray-600">
            {isConnected ? 'Connected' : 'Disconnected'}
          </span>
        </div>
      </div>

      {/* Move Last Prediction above the camera feed and remove mb-10 */}
      {lastDetection && (
        <div className="p-4 bg-blue-50 rounded-lg mb-4">
          <h3 className="font-medium mb-1">Last Prediction</h3>
          <div className="text-sm text-gray-600">
            <p>Product: {lastDetection.product_name || 'N/A'}</p>
            <p>Confidence: {typeof lastDetection.confidence === 'number' && !isNaN(lastDetection.confidence)
              ? (lastDetection.confidence * 100).toFixed(1) + '%'
              : 'N/A'}</p>
          </div>
        </div>
      )}

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
    </div>
  );
};

export default CameraFeed;