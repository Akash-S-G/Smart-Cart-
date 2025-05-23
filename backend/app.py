# install first:
# pip install quart==0.19.4 quart-cors==0.7.0 hypercorn==0.15.0 pillow tensorflow websockets

import io
import json
from PIL import Image
import numpy as np
import os
from tensorflow.keras.models import load_model, Sequential
from tensorflow.keras.layers import Dense
from quart import Quart, send_from_directory, render_template, websocket
from quart_cors import cors
import jwt
import datetime
import base64
import asyncio
import websockets
import logging
from hypercorn.config import Config
from hypercorn.asyncio import serve

# Enable detailed logging
logging.basicConfig(level=logging.DEBUG)

# Constants and Configuration
IMG_W, IMG_H = 224, 224
IMAGE_FOLDER = "received_images"
latest_filename = None

# Create image folder if not exists
os.makedirs(IMAGE_FOLDER, exist_ok=True)

app = Quart(__name__)
app = cors(app)  # Updated CORS setup

# JWT Configuration
app.config['JWT_SECRET_KEY'] = os.environ.get('JWT_SECRET_KEY', 'your-secret-key')

print("🟢 Loading ML model and configurations...")

# Create a simple placeholder model if the real model is not found
def create_placeholder_model():
    print("Creating placeholder model...")
    model = Sequential([
        Dense(10, activation='softmax', input_shape=(IMG_W * IMG_H * 3,))
    ])
    model.compile(optimizer='adam', loss='categorical_crossentropy')
    return model

# Try to load the real model, fall back to placeholder if not found
try:
    print("Loading the trained model...")
    model = load_model("product_model3_finetuned.h5")
    print("✅ Model loaded successfully!")
except Exception as e:
    print(f"⚠️ Could not load the trained model: {str(e)}")
    print("Using placeholder model for testing.")
    model = create_placeholder_model()

# Create a placeholder class indices if file not found
try:
    print("Loading class indices...")
    with open("class_indices.json", "r") as f:
        index_to_class = json.load(f)
    print(f"✅ Loaded {len(index_to_class)} classes")
except Exception as e:
    print(f"⚠️ Could not load class indices: {str(e)}")
    print("Using placeholder classes.")
    index_to_class = {f"product_{i}": i for i in range(10)}

def preprocess_image(img_bytes):
    try:
        print("Processing image...")
        img = Image.open(io.BytesIO(img_bytes)).convert("RGB")
        img = img.resize((IMG_W, IMG_H))
        arr = np.array(img, dtype=np.float32) / 255.0
        return np.expand_dims(arr, axis=0)
    except Exception as e:
        print(f"⚠️ Error preprocessing image: {str(e)}")
        raise

def process_frame(img_bytes, cart_id=None):
    """Common function to process frames from WebSocket"""
    try:
        # Save image to file
        filename = f"{IMAGE_FOLDER}/latest.jpg"
        with open(filename, "wb") as f:
            f.write(img_bytes)
        global latest_filename
        latest_filename = filename
        print(f"💾 Saved image as {filename}")

        # Process image and get prediction
        input_tensor = preprocess_image(img_bytes)
        preds = model.predict(input_tensor)[0]
        idx = int(np.argmax(preds))
        cls = list(index_to_class.keys())[list(index_to_class.values()).index(idx)]
        confidence = float(preds[idx])

        return {
            "class": cls,
            "confidence": round(confidence, 3),
            "cart_id": cart_id
        }
    except Exception as e:
        print(f"❌ Error processing frame: {str(e)}")
        return {"error": str(e)}

@app.route('/')
async def hello():
    return {"message": "SmartCart API is running!"}

@app.route('/preview')
async def preview():
    return await render_template("preview.html")

@app.route('/latest.jpg')
async def serve_image():
    return await send_from_directory(IMAGE_FOLDER, "latest.jpg")

# WebSocket handler
async def handle_websocket(websocket, path):
    print(f"🔌 WebSocket client connected on {path}")
    try:
        async for message in websocket:
            try:
                data = json.loads(message)
                if "image" not in data:
                    await websocket.send(json.dumps({"error": "No image key"}))
                    continue

                b64 = data["image"].split(",")[1] if "," in data["image"] else data["image"]
                img_bytes = base64.b64decode(b64)
                
                result = process_frame(img_bytes, data.get('cart_id'))
                await websocket.send(json.dumps(result))
                
            except Exception as e:
                print(f"❌ Error processing WebSocket message: {str(e)}")
                await websocket.send(json.dumps({"error": str(e)}))
    except Exception as e:
        print(f"❌ WebSocket connection error: {str(e)}")

async def run_websocket_server():
    print("🚀 Starting WebSocket server on port 5001...")
    async with websockets.serve(handle_websocket, "0.0.0.0", 5001):
        await asyncio.Future()  # run forever

if __name__ == '__main__':
    print("\n🚀 Starting SmartCart server...")
    print("📡 Connection Options:")
    print("1. WebSocket:")
    print("   - URL: ws://localhost:5001")
    print("   - Protocol: Standard WebSocket")
    print("   - Send JSON with 'image' and optional 'cart_id'")
    print(f"\n📁 Image folder: {os.path.abspath(IMAGE_FOLDER)}")
    print(f"🌐 Preview available at: http://localhost:5000/preview\n")
    
    # Configure Hypercorn
    config = Config()
    config.bind = ["0.0.0.0:5000"]
    config.use_reloader = True
    
    # Create tasks for both servers
    websocket_task = asyncio.create_task(run_websocket_server())
    http_task = asyncio.create_task(serve(app, config))
    
    # Run both servers
    asyncio.run(asyncio.gather(websocket_task, http_task))
