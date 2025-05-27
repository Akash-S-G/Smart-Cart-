# install first:
# pip install quart==0.19.4 quart-cors==0.7.0 hypercorn==0.15.0 pillow tensorflow websockets

import io
import json
from PIL import Image
import numpy as np
import os
from tensorflow.keras.models import load_model, Sequential
from tensorflow.keras.layers import Dense
from quart import Quart, send_from_directory, render_template, websocket, request, jsonify, make_response
from quart_cors import cors
import jwt
import datetime
import base64
import asyncio
import websockets
import logging
from hypercorn.config import Config
from hypercorn.asyncio import serve
from tensorflow.keras.preprocessing.image import img_to_array
import socket
from functools import wraps
import aiohttp

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Quart app
app = Quart(__name__)
app = cors(app)

# Constants
JWT_SECRET = "your-secret-key"  # Change this in production
WEBSOCKET_PORT = 5001
HTTP_PORT = 5000
IMAGE_FOLDER = "received_images"
MODEL_PATH = "product_model3_finetuned.h5"

# Mock user database (replace with real database in production)
USERS = {
    "admin": {
        "password": "admin123",  # In production, use hashed passwords
        "role": "admin"
    },
    "user": {
        "password": "user123",
        "role": "user"
    }
}

# Get local IP address
def get_local_ip():
    try:
        # Create a socket object
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        # Connect to an external server (doesn't actually send any data)
        s.connect(("8.8.8.8", 80))
        # Get the local IP address
        local_ip = s.getsockname()[0]
        s.close()
        return local_ip
    except Exception:
        return "localhost"

SERVER_IP = get_local_ip()

# Ensure image folder exists
os.makedirs(IMAGE_FOLDER, exist_ok=True)

print("🟢 Loading ML model and configurations...")

# Load the model
print("Loading the trained model...")
try:
    model = load_model(MODEL_PATH)
    print("✅ Model loaded successfully!")
except Exception as e:
    print(f"⚠️ Error loading model: {e}")
    model = Sequential()  # Empty model as placeholder
    print("⚠️ Using placeholder model")

# Load class indices
print("Loading class indices...")
try:
    with open("class_indices.json", "r") as f:
        class_indices = json.load(f)
except Exception as e:
    print(f"⚠️ Could not load class indices: {e}")
    class_indices = {str(i): f"class_{i}" for i in range(10)}  # Placeholder
    print("Using placeholder classes.")

def preprocess_image(image_data):
    """Preprocess image data for model prediction."""
    try:
        # Convert base64 to image
        if isinstance(image_data, str):
            # Remove data URL prefix if present
            if "base64," in image_data:
                image_data = image_data.split("base64,")[1]
            image_data = base64.b64decode(image_data)
        
        # Open and preprocess image
        img = Image.open(io.BytesIO(image_data))
        img = img.resize((224, 224))  # Adjust size according to your model
        img_array = img_to_array(img)
        img_array = np.expand_dims(img_array, axis=0)
        img_array = img_array / 255.0  # Normalize
        
        return img_array
    except Exception as e:
        logger.error(f"Error preprocessing image: {e}")
        return None

def save_image(image_data, cart_id=None):
    """Save received image to disk."""
    try:
        if isinstance(image_data, str):
            if "base64," in image_data:
                image_data = image_data.split("base64,")[1]
            image_data = base64.b64decode(image_data)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{timestamp}_{cart_id}.jpg" if cart_id else f"{timestamp}.jpg"
        filepath = os.path.join(IMAGE_FOLDER, filename)
        
        with open(filepath, "wb") as f:
            f.write(image_data)
        
        return filepath
    except Exception as e:
        logger.error(f"Error saving image: {e}")
        return None

def generate_token(cart_id):
    """Generate JWT token for cart authentication."""
    expiration = datetime.utcnow() + timedelta(days=1)
    return jwt.encode(
        {"cart_id": cart_id, "exp": expiration},
        JWT_SECRET,
        algorithm="HS256"
    )

async def process_image(image_data, cart_id=None):
    """Process image and return predictions."""
    try:
        # Save image
        filepath = save_image(image_data, cart_id)
        if not filepath:
            return {"error": "Failed to save image"}

        # Preprocess image
        processed_img = preprocess_image(image_data)
        if processed_img is None:
            return {"error": "Failed to process image"}

        # Make prediction
        predictions = model.predict(processed_img)
        predicted_class = str(np.argmax(predictions[0]))
        confidence = float(np.max(predictions[0]))

        # Get class label
        class_label = class_indices.get(predicted_class, f"Unknown ({predicted_class})")

        return {
            "success": True,
            "class": class_label,
            "confidence": confidence,
            "file_path": filepath
        }
    except Exception as e:
        logger.error(f"Error processing image: {e}")
        return {"error": str(e)}

def token_required(f):
    @wraps(f)
    async def decorated(*args, **kwargs):
        token = None
        auth_header = (await request.headers).get('Authorization')
        
        if auth_header and auth_header.startswith('Bearer '):
            token = auth_header.split(' ')[1]
        
        if not token:
            return await make_response(jsonify({'message': 'Token is missing'}), 401)
        
        try:
            data = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
            current_user = USERS.get(data['username'])
            if not current_user:
                return await make_response(jsonify({'message': 'Invalid token'}), 401)
        except jwt.ExpiredSignatureError:
            return await make_response(jsonify({'message': 'Token has expired'}), 401)
        except jwt.InvalidTokenError:
            return await make_response(jsonify({'message': 'Invalid token'}), 401)
        
        return await f(current_user, *args, **kwargs)
    return decorated

@app.route("/login", methods=["POST"])
async def login():
    """Handle user login and return JWT token."""
    try:
        data = await request.get_json()
        username = data.get('username')
        password = data.get('password')
        
        if not username or not password:
            return await make_response(jsonify({'message': 'Missing username or password'}), 400)
        
        user = USERS.get(username)
        if not user or user['password'] != password:  # In production, use proper password hashing
            return await make_response(jsonify({'message': 'Invalid credentials'}), 401)
        
        # Generate token
        token = jwt.encode({
            'username': username,
            'role': user['role'],
            'exp': datetime.utcnow() + timedelta(hours=24)
        }, JWT_SECRET, algorithm="HS256")
        
        return await make_response(jsonify({
            'message': 'Login successful',
            'token': token,
            'username': username,
            'role': user['role']
        }), 200)
    except Exception as e:
        logger.error(f"Login error: {e}")
        return await make_response(jsonify({'message': 'Internal server error'}), 500)

@app.route("/check-auth")
@token_required
async def check_auth(current_user):
    """Check if the user is authenticated."""
    return await make_response(jsonify({
        'message': 'Authenticated',
        'username': current_user['username'],
        'role': current_user['role']
    }), 200)

@app.route("/")
async def index():
    """Render the preview page."""
    return await render_template("preview.html", server_ip=SERVER_IP)

@app.route("/preview")
@token_required
async def preview(current_user):
    """Render the preview page."""
    return await render_template("preview.html", server_ip=SERVER_IP)

@app.route("/images/<path:filename>")
@token_required
async def serve_image(current_user, filename):
    """Serve images from the received_images directory."""
    return await app.send_file(os.path.join(IMAGE_FOLDER, filename))

async def websocket_handler(websocket, path):
    """Handle WebSocket connections from ESP32 cameras."""
    try:
        logger.info(f"New WebSocket connection from {websocket.remote_address}")
        
        async for message in websocket:
            try:
                # Parse the JSON message
                data = json.loads(message)
                cart_id = data.get('cart_id')
                
                if not cart_id:
                    logger.warning("Received message without cart_id")
                    continue
                
                # Handle chunked images
                if 'chunk' in data:
                    # Forward the chunk to Socket.IO clients
                    await forward_to_socketio(data)
                    
                    # If this is the final chunk, process the complete image
                    if data.get('final', False):
                        logger.info(f"Completed frame from cart {cart_id}")
                
            except json.JSONDecodeError:
                logger.error("Failed to parse WebSocket message")
            except Exception as e:
                logger.error(f"Error processing message: {str(e)}")
                
    except websockets.exceptions.ConnectionClosed:
        logger.info("WebSocket connection closed")
    except Exception as e:
        logger.error(f"WebSocket handler error: {str(e)}")

async def forward_to_socketio(data):
    """Forward the frame data to Socket.IO clients."""
    try:
        # Make a POST request to the Socket.IO server
        async with aiohttp.ClientSession() as session:
            async with session.post(f'http://localhost:{HTTP_PORT}/esp32_ws_forward', 
                                  json=data) as response:
                if response.status != 200:
                    logger.error(f"Failed to forward frame: {response.status}")
    except Exception as e:
        logger.error(f"Error forwarding to Socket.IO: {str(e)}")

async def run_servers():
    """Run both the WebSocket server and Quart app."""
    ws_server = await websockets.serve(websocket_handler, "0.0.0.0", WEBSOCKET_PORT)
    
    print(f"\n🚀 Starting SmartCart server...")
    print(f"📡 Connection Options:")
    print(f"   - Send JSON with 'image' and optional 'cart_id'")
    print(f"\n📁 Image folder: {os.path.abspath(IMAGE_FOLDER)}")
    print(f"🌐 Server IP: {SERVER_IP}")
    print(f"🌐 Preview available at: http://{SERVER_IP}:{HTTP_PORT}/preview")
    print(f"🔌 WebSocket URL: ws://{SERVER_IP}:{WEBSOCKET_PORT}\n")
    
    await app.run_task(host="0.0.0.0", port=HTTP_PORT)
    await ws_server.wait_closed()

if __name__ == "__main__":
    SERVER_IP = get_local_ip()
    
    # Create image folder if it doesn't exist
    os.makedirs(IMAGE_FOLDER, exist_ok=True)
    
    # Run both servers
    asyncio.run(run_servers())
