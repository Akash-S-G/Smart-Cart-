import React, { useEffect, useState, useRef } from 'react';
import { io } from 'socket.io-client';
import { toast } from 'react-hot-toast';
import useCartStore from '../stores/cartStore';

const API_URL = process.env.REACT_APP_API_URL || 'http://192.168.74.207:5000';

const CameraFeed = ({ cartId }) => {
  const [isConnected, setIsConnected] = useState(false);
  const [lastDetection, setLastDetection] = useState(null);
  const [lastAddedProduct, setLastAddedProduct] = useState({ id: null, confidence: 0 });
  const [useWebcam, setUseWebcam] = useState(false);
  const socketRef = useRef(null);
  const imageRef = useRef(null);
  const videoRef = useRef(null);
  const addItem = useCartStore(state => state.addItem);

  // Webcam stream logic
  useEffect(() => {
    let stream;
    if (useWebcam && videoRef.current) {
      navigator.mediaDevices.getUserMedia({ video: true })
        .then(s => {
          stream = s;
          videoRef.current.srcObject = stream;
        })
        .catch(err => {
          toast.error('Webcam access denied or not available');
        });
    }
    return () => {
      if (stream) {
        stream.getTracks().forEach(track => track.stop());
      }
    };
  }, [useWebcam]);

  // --- Webcam prediction logic ---
  useEffect(() => {
    if (!useWebcam) return;
    let interval;
    const captureAndPredict = async () => {
      if (!videoRef.current) return;
      const video = videoRef.current;
      const canvas = document.createElement('canvas');
      canvas.width = video.videoWidth || 224;
      canvas.height = video.videoHeight || 224;
      const ctx = canvas.getContext('2d');
      ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
      const dataUrl = canvas.toDataURL('image/jpeg');
      const base64 = dataUrl.split(',')[1];
      try {
        const res = await fetch(`${API_URL}/predict_product`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ cart_id: cartId, image_base64: base64 })
        });
        const data = await res.json();
        if (data && typeof data.confidence !== 'undefined' && data.product_name) {
          setLastDetection(data);
          if (
            data.product_name !== 'Unknown or Not Recognized' &&
            typeof data.confidence === 'number' &&
            data.confidence >= 0.85
          ) {
            if (
              lastAddedProduct.id !== data.product_id ||
              lastAddedProduct.confidence < 0.85
            ) {
              const price = Math.floor(Math.random() * 100) + 1;
              addItem({
                id: data.product_id,
                name: data.product_name,
                price,
                confidence: data.confidence
              });
              setLastAddedProduct({ id: data.product_id, confidence: data.confidence });
              toast.success(`Added to cart: ${data.product_name} (₹${price})`);
            }
          } else {
            if (
              lastAddedProduct.id === data.product_id &&
              data.confidence < 0.85
            ) {
              setLastAddedProduct({ id: null, confidence: 0 });
            }
          }
        }
      } catch (e) {
        // ignore
      }
    };
    interval = setInterval(captureAndPredict, 1000);
    return () => clearInterval(interval);
  }, [useWebcam, cartId, addItem, lastAddedProduct]);

  // --- ESP32 polling logic ---
  useEffect(() => {
    if (useWebcam) return;
    let lastImageUrl = null;
    let lastConnected = false;
    const fetchImage = () => {
      fetch(`${API_URL}/latest_image?_t=${Date.now()}`)
        .then(res => {
          if (!res.ok) throw new Error('No image');
          if (!lastConnected) {
            setIsConnected(true);
            lastConnected = true;
          }
          return res.blob();
        })
        .then(blob => {
          if (imageRef.current) {
            if (lastImageUrl) URL.revokeObjectURL(lastImageUrl);
            lastImageUrl = URL.createObjectURL(blob);
            imageRef.current.src = lastImageUrl;
          }
        })
        .catch(() => {
          if (imageRef.current) imageRef.current.src = '';
          if (lastConnected) {
            setIsConnected(false);
            lastConnected = false;
          }
        });
    };
    fetchImage();
    const interval = setInterval(fetchImage, 200);
    return () => {
      clearInterval(interval);
      if (lastImageUrl) URL.revokeObjectURL(lastImageUrl);
    };
  }, [useWebcam]);

  useEffect(() => {
    if (useWebcam) return;
    const fetchPrediction = () => {
      fetch(`${API_URL}/latest_prediction`)
        .then(res => res.json())
        .then(data => {
          if (data && typeof data.confidence !== 'undefined' && data.product_name) {
            setLastDetection(data);
            if (
              data.product_name !== 'Unknown or Not Recognized' &&
              typeof data.confidence === 'number' &&
              data.confidence >= 0.85
            ) {
              if (
                lastAddedProduct.id !== data.product_id ||
                lastAddedProduct.confidence < 0.85
              ) {
                const price = Math.floor(Math.random() * 100) + 1;
                addItem({
                  id: data.product_id,
                  name: data.product_name,
                  price,
                  confidence: data.confidence
                });
                setLastAddedProduct({ id: data.product_id, confidence: data.confidence });
                toast.success(`Added to cart: ${data.product_name} (₹${price})`);
              }
            } else {
              if (
                lastAddedProduct.id === data.product_id &&
                data.confidence < 0.85
              ) {
                setLastAddedProduct({ id: null, confidence: 0 });
              }
            }
          }
        })
        .catch(() => {});
    };
    fetchPrediction();
    const interval = setInterval(fetchPrediction, 1000);
    return () => clearInterval(interval);
  }, [cartId, addItem, lastAddedProduct, useWebcam]);

  return (
    <div className="bg-white p-4 rounded-lg shadow">
      <div className="mb-4">
        <h2 className="text-xl font-semibold mb-2">Camera Feed</h2>
        <div className="flex items-center space-x-2 mb-2">
          <div
            className={`w-3 h-3 rounded-full ${isConnected ? 'bg-green-500' : 'bg-red-500'}`}
          />
          <span className="text-sm text-gray-600">
            {isConnected ? 'Connected' : 'Disconnected'}
          </span>
        </div>
        <div className="mb-2">
          <button
            className={`px-3 py-1 rounded mr-2 ${!useWebcam ? 'bg-blue-500 text-white' : 'bg-gray-200'}`}
            onClick={() => setUseWebcam(false)}
          >
            ESP32 Camera
          </button>
          <button
            className={`px-3 py-1 rounded ${useWebcam ? 'bg-blue-500 text-white' : 'bg-gray-200'}`}
            onClick={() => setUseWebcam(true)}
          >
            Webcam / Mobile Camera
          </button>
        </div>
      </div>
      {lastDetection && (
        <div className="p-3 bg-blue-50 rounded-lg ">
          <h3 className="font-medium mb-1">Last Prediction</h3>
          <div className="text-sm text-gray-600">
            <p>Product: {lastDetection.product_name || 'N/A'}</p>
            <p>
              Confidence: {typeof lastDetection.confidence === 'number' && !isNaN(lastDetection.confidence)
                ? (lastDetection.confidence * 100).toFixed(1) + '%'
                : 'N/A'}
            </p>
          </div>
        </div>
      )}
      <div className="relative aspect-video mx-auto bg-gray-100 rounded-lg overflow-hidden mt-4 w-full max-w-2xl">
        {!useWebcam ? (
          <img
            ref={imageRef}
            alt="Camera feed"
            className="w-full h-full object-cover"
          />
        ) : (
          <video
            ref={videoRef}
            autoPlay
            playsInline
            className="w-full h-full object-cover"
          />
        )}
        {!isConnected && !useWebcam && (
          <div className="absolute inset-0 flex items-center justify-center bg-gray-900 bg-opacity-50 text-white">
            Connecting to camera...
          </div>
        )}
      </div>

      
    </div>
  );
};

export default CameraFeed;