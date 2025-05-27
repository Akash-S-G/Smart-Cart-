from flask import Blueprint, request, jsonify
from flask_socketio import emit
import base64
import cv2
import numpy as np
from PIL import Image
import io
import qrcode
from pyzbar.pyzbar import decode
import tensorflow as tf
from datetime import datetime
import json
import os

camera = Blueprint('camera', __name__)

# Store connected carts and their sessions
connected_carts = {}

# Load the product detection model
MODEL_PATH = 'ml_models/weights/product_model3_finetuned.h5'
try:
    model = tf.keras.models.load_model(MODEL_PATH)
    print(f"Loaded AI model from {MODEL_PATH}")
except Exception as e:
    print(f"Warning: Product detection model not found at {MODEL_PATH}. Creating a placeholder model. Error: {e}")
    # Create a simple placeholder model
    model = tf.keras.Sequential([
        tf.keras.layers.Input(shape=(224, 224, 3)),
        tf.keras.layers.Conv2D(16, 3, activation='relu'),
        tf.keras.layers.GlobalAveragePooling2D(),
        tf.keras.layers.Dense(10, activation='softmax')
    ])

# Load product database
def load_products():
    try:
        with open('backend/data/products.json', 'r') as f:
            return json.load(f)['products']
    except:
        print("Warning: Products database not found.")
        return []

products_db = load_products()

def get_product_details(product_id):
    """Get product details from database"""
    return next((product for product in products_db if product['id'] == product_id), None)

def process_frame(frame_data):
    """Process incoming frame for product detection"""
    # Convert base64 to image
    img_bytes = base64.b64decode(frame_data)
    nparr = np.frombuffer(img_bytes, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    
    # Detect QR codes
    qr_detections = detect_qr_codes(img)
    if qr_detections:
        return qr_detections
    
    # If no QR codes found, try product detection
    return detect_products(img)

def detect_qr_codes(img):
    """Detect QR codes in image"""
    detections = []
    decoded_objects = decode(img)
    
    for obj in decoded_objects:
        data = obj.data.decode('utf-8')
        product = get_product_details(data)
        if product:
            detections.append({
                'product_id': data,
                'name': product['name'],
                'price': product['price'],
                'confidence': 1.0,
                'detection_type': 'qr_code'
            })
    
    return detections

def detect_products(img):
    """Detect products using the trained model"""
    # Preprocess image
    img = cv2.resize(img, (224, 224))
    img = img / 255.0
    img = np.expand_dims(img, axis=0)
    
    # Get predictions
    predictions = model.predict(img)[0]
    max_pred_idx = int(np.argmax(predictions))
    confidence = float(predictions[max_pred_idx])
    
    if confidence > 0.7:  # Confidence threshold
        product_id = f"product_{max_pred_idx}"
        product = get_product_details(product_id)
        if product:
            return [{
                'product_id': product_id,
                'name': product['name'],
                'price': product['price'],
                'confidence': confidence,
                'detection_type': 'model'
            }]
    
    return []

@camera.route('/connect', methods=['POST'])
def connect_cart():
    """Handle cart connection"""
    data = request.json
    cart_id = data.get('cart_id')
    
    if not cart_id:
        return jsonify({'error': 'Cart ID required'}), 400
    
    connected_carts[cart_id] = {
        'connected_at': datetime.now(),
        'last_detection': None
    }
    
    return jsonify({
        'message': f'Cart {cart_id} connected successfully',
        'status': 'connected'
    })

@camera.route('/ws_auth', methods=['POST'])
def ws_auth():
    data = request.get_json(force=True)
    cart_id = data.get('cart_id')
    if not cart_id:
        return jsonify({'error': 'Cart ID required'}), 400
    # You can add more authentication logic here if needed
    emit('connection_confirmed', {'status': 'connected', 'cart_id': cart_id, 'type': 'esp32'}, broadcast=True)
    return jsonify({'message': 'ESP32 authenticated', 'cart_id': cart_id})

def handle_frame(data):
    """Handle incoming frame from ESP32"""
    cart_id = data.get('cart_id')
    image_data = data.get('image')
    
    if not cart_id or not image_data:
        return
    
    # Process frame
    detections = process_frame(image_data)
    
    if detections:
        # Emit detection results back to the cart
        emit('cart_update', {
            'cart_id': cart_id,
            'cart_updated': True,
            'detections': detections,
            'timestamp': datetime.now().isoformat()
        })
        
        # Update cart's last detection
        if cart_id in connected_carts:
            connected_carts[cart_id]['last_detection'] = datetime.now()
            
        # Emit to frontend clients
        emit('product_detected', {
            'cart_id': cart_id,
            'detections': detections
        }, broadcast=True)