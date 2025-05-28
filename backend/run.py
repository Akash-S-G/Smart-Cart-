import eventlet
# Disable eventlet DNS monkey patching to fix Gemini API DNS errors on Windows
# See: https://github.com/eventlet/eventlet/issues/401
# This allows requests to use the system DNS resolver
# eventlet.monkey_patch(dns=False)
# import eventlet
# eventlet.patcher.monkey_patch_all(socket=True, select=True, time=True, thread=True, os=True)


from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from flask_socketio import SocketIO, emit
import datetime
import logging
from collections import defaultdict
import time
import base64
import cv2
import numpy as np
from PIL import Image
import io
import socket
import sys
import os
import json
import threading
import requests
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv(os.path.join(os.path.dirname(__file__), '.env'))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def get_available_port(start_port=5000, max_port=5010):
    for port in range(start_port, max_port + 1):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(('0.0.0.0', port))
                return port
        except OSError:
            continue
    raise RuntimeError('No available ports in range')

app = Flask(__name__)
CORS(app)

# Connection management
active_connections = {}
cart_connections = defaultdict(set)
connection_attempts = defaultdict(lambda: {"count": 0, "last_attempt": 0})

# Rate limiting configuration
RATE_LIMIT_WINDOW = 300
MAX_CONNECTIONS_PER_CART = 3
RECONNECTION_COOLDOWN = 0.5

# SocketIO Configuration
socketio = SocketIO(
    app,
    cors_allowed_origins="*",
    async_mode='eventlet',
    logger=True,
    engineio_logger=True,
    ping_timeout=120,
    ping_interval=25,
    max_http_buffer_size=50 * 1024 * 1024,
    reconnection=True,
    reconnection_attempts=10,
    reconnection_delay=1000,
    reconnection_delay_max=5000,
    transports=['websocket', 'polling'],
    allow_upgrades=True,
    handle_bad_request=True,
    binary=True,
    manage_session=True,
    monitor_clients=True,
    cookie=None,
    engineio_logger_level='debug'
)

def notify_browser_clients(cart_id, event, data):
    browser_sids = [sid for sid, conn in active_connections.items()
                   if conn['cart_id'] == cart_id and conn['type'] == 'browser']
    data.update({
        'cart_id': cart_id,
        'timestamp': datetime.datetime.now().isoformat()
    })
    for browser_sid in browser_sids:
        socketio.emit(event, data, room=browser_sid)

frame_buffers = defaultdict(lambda: {
    'buffer': '',
    'last_chunk': -1,
    'timestamp': time.time(),
    'chunks_received': 0,
    'total_chunks': 0
})

def can_connect(cart_id):
    now = time.time()
    cart_data = connection_attempts[cart_id]
    if now - cart_data["last_attempt"] > RATE_LIMIT_WINDOW:
        cart_data["count"] = 0
    if now - cart_data["last_attempt"] < RECONNECTION_COOLDOWN:
        return False
    if len(cart_connections[cart_id]) >= MAX_CONNECTIONS_PER_CART:
        return False
    cart_data["count"] += 1
    cart_data["last_attempt"] = now
    return True

@app.route('/')
def hello():
    return {"message": "SmartCart API is running!"}

RECEIVED_IMAGE_DIR = 'ml_models/inference/received_images'
os.makedirs(RECEIVED_IMAGE_DIR, exist_ok=True)
latest_image_path = os.path.join(RECEIVED_IMAGE_DIR, 'latest.jpg')
latest_image_lock = threading.Lock()

# Store the latest prediction result
default_prediction = {'product_id': None, 'product_name': None, 'confidence': None, 'cart_id': None}
latest_prediction = default_prediction.copy()
latest_prediction_lock = threading.Lock()

def call_gemini_api(image_b64):
    api_key = os.environ.get('GEMINI_API_KEY')
    if not api_key:
        logger.error('GEMINI_API_KEY not set!')
        return None
    # Use the new Gemini model endpoint
    url = 'https://generativelanguage.googleapis.com/v1/models/gemini-1.5-flash:generateContent?key=' + api_key
    headers = {'Content-Type': 'application/json'}
    payload = {
        "contents": [
            {
                "parts": [
                    {"text": "What product is in this image?think only about products in any shopping store or grocery items  Return a JSON with product_name and confidence (0-1)."},
                    {"inlineData": {"mimeType": "image/jpeg", "data": image_b64}}
                ]
            }
        ]
    }
    try:
        resp = requests.post(url, headers=headers, json=payload, timeout=8)
        logger.info(f'[Gemini API] Status: {resp.status_code}, Response: {resp.text}')
        resp.raise_for_status()
        data = resp.json()
        # Parse Gemini response for product_name and confidence
        text = data['candidates'][0]['content']['parts'][0]['text']
        import re, json as pyjson
        match = re.search(r'\{.*\}', text, re.DOTALL)
        if match:
            result = pyjson.loads(match.group(0))
            return {
                'product_name': result.get('product_name'),
                'confidence': float(result.get('confidence', 0)),
                'source': 'gemini'
            }
        else:
            logger.error(f'[Gemini API] No JSON found in response text: {text}')
    except Exception as e:
        logger.error(f'Gemini API error: {e}')
    return None

def async_gemini_update(image_b64, cart_id, confidence_local):
    gemini_result = call_gemini_api(image_b64)
    if gemini_result and gemini_result['confidence'] > confidence_local:
        best_result = {
            'cart_id': cart_id,
            'product_id': None,
            'product_name': gemini_result['product_name'],
            'confidence': gemini_result['confidence']
            # 'source' removed
        }
        with latest_prediction_lock:
            latest_prediction.update(best_result)
        logger.info(f"[Async Gemini] Updated prediction: {best_result['product_name']} | Confidence: {best_result['confidence']:.3f} | Source: gemini")

@app.route('/predict_product', methods=['POST'])
def predict_product():
    try:
        import time as _time
        start_time = _time.time()
        data = request.get_json()
        cart_id = data.get('cart_id')
        image_b64 = data.get('image_base64') or data.get('image')
        if not cart_id or not image_b64:
            return jsonify({'error': 'cart_id and image are required'}), 400
        # Decode base64 image
        img_bytes = base64.b64decode(image_b64)
        nparr = np.frombuffer(img_bytes, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        # Save the image as latest.jpg (thread-safe)
        with latest_image_lock:
            cv2.imwrite(latest_image_path, img)
        # --- Local model prediction ---
        img_resized = cv2.resize(img, (224, 224))
        img_resized = img_resized / 255.0
        img_resized = np.expand_dims(img_resized, axis=0)
        model_path = os.path.join(os.path.dirname(__file__), '..', 'ml_models', 'weights', 'product_model3_finetuned.h5')
        model_path = os.path.abspath(model_path)
        import tensorflow as tf
        model = tf.keras.models.load_model(model_path)
        predictions = model.predict(img_resized)[0]
        max_pred_idx = int(np.argmax(predictions))
        confidence_local = float(predictions[max_pred_idx] ) 
        class_indices_path = os.path.join(os.path.dirname(__file__), '..', 'ml_models', 'training', 'class_indices.json')
        with open(class_indices_path, 'r') as f:
            class_indices = json.load(f)
        idx_to_class = {int(v): k for k, v in class_indices.items()}
        product_name_local = idx_to_class.get(max_pred_idx, 'Unknown or Not Recognized')
        local_result = {
            'cart_id': cart_id,
            'product_id': max_pred_idx,
            'product_name': product_name_local,
            'confidence': confidence_local
        }
        # Store the local prediction immediately
        with latest_prediction_lock:
            latest_prediction.update(local_result)
        elapsed = _time.time() - start_time
        logger.info(f"Predicted product: {local_result['product_name']} | Confidence: {local_result['confidence']:.3f} | Source: local | Time: {elapsed:.2f}s")
        # Start Gemini API call in a background thread
        threading.Thread(target=async_gemini_update, args=(image_b64, cart_id, confidence_local), daemon=True).start()
        return jsonify(local_result)
    except Exception as e:
        logger.error(f'/predict_product error: {str(e)}')
        return jsonify({'error': str(e)}), 500

@app.route('/latest_image')
def latest_image():
    # Serve the latest image as JPEG
    if os.path.exists(latest_image_path):
        return send_file(latest_image_path, mimetype='image/jpeg')
    else:
        return jsonify({'error': 'No image available'}), 404

@app.route('/latest_prediction', methods=['GET'])
def get_latest_prediction():
    with latest_prediction_lock:
        if latest_prediction['product_id'] is not None:
            return jsonify(latest_prediction)
        else:
            return jsonify({'error': 'No prediction available'}), 404

# --- AUTHENTICATION HANDLER FOR ESP32 ---
@socketio.on('authenticate')
def handle_authentication(data):
    cart_id = data.get('cart_id')
    if not cart_id:
        emit('authentication_failed', {'reason': 'No cart_id provided'})
        return
    # Here you can add your own validation logic for cart_id
    emit('connection_confirmed', {
        'status': 'connected',
        'cart_id': cart_id,
        'client_type': 'esp32'
    }, room=request.sid)
    logger.info(f'[SocketIO] Sent connection_confirmed to ESP32 cart {cart_id}')

@socketio.on('connect')
def handle_connect(auth=None):
    try:
        transport = request.args.get('transport', '')
        if transport != 'websocket':
            logger.warning(f'[SocketIO] Rejected non-WebSocket transport: {transport}')
            return False
        cart_id = request.args.get('cart_id')
        if not cart_id and auth:
            if not isinstance(auth, dict):
                logger.warning('[SocketIO] Invalid auth data format')
                return False
            cart_id = auth.get('cart_id')
        if not cart_id:
            logger.warning('[SocketIO] Connection attempt without cart_id')
            return False
        if not can_connect(cart_id):
            logger.warning(f'[SocketIO] Connection rejected for cart_id {cart_id} (rate limit)')
            return False
        client_type = 'esp32' if auth else 'browser'
        logger.info(f'[SocketIO] {client_type} client connected with cart_id: {cart_id}')
        if cart_id not in cart_connections:
            cart_connections[cart_id] = set()
        active_connections[request.sid] = {
            'cart_id': cart_id,
            'connected_at': datetime.datetime.now(),
            'type': client_type,
            'last_activity': datetime.datetime.now(),
            'is_camera_connected': client_type == 'esp32'
        }
        cart_connections[cart_id].add(request.sid)
        if client_type == 'esp32':
            socketio.emit('camera_status', {
                'cart_id': cart_id,
                'status': 'connected',
                'timestamp': datetime.datetime.now().isoformat()
            }, room=cart_id)
        elif client_type == 'browser':
            has_camera = any(conn['type'] == 'esp32' and conn['cart_id'] == cart_id
                           for conn in active_connections.values())
            socketio.emit('camera_status', {
                'cart_id': cart_id,
                'status': 'connected' if has_camera else 'waiting_for_camera',
                'timestamp': datetime.datetime.now().isoformat()
            }, room=request.sid)
        # Do not emit connection_confirmed here for ESP32, wait for authenticate event
        if client_type == 'browser':
            socketio.emit('connection_confirmed', {
                'status': 'connected',
                'cart_id': cart_id,
                'sid': request.sid,
                'max_connections': MAX_CONNECTIONS_PER_CART,
                'cooldown': RECONNECTION_COOLDOWN,
                'client_type': client_type
            }, room=request.sid)
        logger.info(f'[SocketIO] Sent connection_confirmed to sid={request.sid}, cart_id={cart_id}, client_type={client_type}')
        return True
    except Exception as e:
        logger.error(f'[SocketIO] Connection error: {str(e)}')
        return False

@socketio.on('disconnect')
def handle_disconnect():
    if request.sid in active_connections:
        disconnecting_conn = active_connections[request.sid]
        cart_id = disconnecting_conn['cart_id']
        client_type = disconnecting_conn['type']
        logger.info(f'[SocketIO] {client_type} client disconnected: {cart_id}')
        cart_connections[cart_id].discard(request.sid)
        if not cart_connections[cart_id]:
            del cart_connections[cart_id]
        if client_type == 'esp32':
            browser_sids = [sid for sid, conn in active_connections.items()
                          if conn['cart_id'] == cart_id and conn['type'] == 'browser']
            for browser_sid in browser_sids:
                socketio.emit('camera_status', {
                    'cart_id': cart_id,
                    'status': 'disconnected',
                    'message': 'Camera connection lost. Waiting for reconnection...',
                    'timestamp': datetime.datetime.now().isoformat()
                }, room=browser_sid)
        del active_connections[request.sid]
    else:
        logger.warning('[SocketIO] Unknown client disconnected')

@socketio.on('esp32_frame')
def handle_esp32_frame(data):
    try:
        cart_id = data.get('cart_id')
        if not cart_id:
            logger.warning('[SocketIO] Received frame without cart_id')
            return
        if request.sid not in active_connections or active_connections[request.sid]['type'] != 'esp32':
            logger.warning(f'[SocketIO] Non-ESP32 client tried to send frame: {request.sid}')
            return
        conn = active_connections[request.sid]
        conn['last_activity'] = datetime.datetime.now()
        conn['is_camera_connected'] = True
        if cart_id in connection_attempts:
            connection_attempts[cart_id]['count'] = 0
        if 'chunk' in data:
            chunk_index = data.get('chunk_index', 0)
            total_chunks = data.get('total_chunks', 1)
            buffer_data = frame_buffers[cart_id]
            if time.time() - buffer_data['timestamp'] > 5:
                logger.warning(f'[SocketIO] Stale buffer detected for cart {cart_id}, resetting')
                buffer_data['buffer'] = ''
                buffer_data['last_chunk'] = -1
                buffer_data['chunks_received'] = 0
                buffer_data['total_chunks'] = total_chunks
            if chunk_index != buffer_data['last_chunk'] + 1:
                logger.warning(f'[SocketIO] Out of order chunk received for cart {cart_id}')
                buffer_data['buffer'] = ''
                buffer_data['last_chunk'] = -1
                buffer_data['chunks_received'] = 0
                return
            buffer_data['buffer'] += data['chunk']
            buffer_data['last_chunk'] = chunk_index
            buffer_data['timestamp'] = time.time()
            buffer_data['chunks_received'] += 1
            if buffer_data['chunks_received'] >= total_chunks:
                try:
                    frame_data = buffer_data['buffer']
                    buffer_data['buffer'] = ''
                    buffer_data['last_chunk'] = -1
                    buffer_data['chunks_received'] = 0
                    socketio.emit('frame_update', {
                        'cart_id': cart_id,
                        'frame': frame_data,
                        'timestamp': datetime.datetime.now().isoformat()
                    }, room=cart_id)
                    logger.info(f'[SocketIO] Complete frame processed for cart {cart_id}')
                except Exception as frame_error:
                    logger.error(f'[SocketIO] Frame processing error: {str(frame_error)}')
                    notify_browser_clients(cart_id, 'frame_error', {
                        'message': 'Error processing camera frame',
                        'error': str(frame_error)
                    })
        else:
            logger.warning('[SocketIO] Received frame without chunk data')
    except Exception as e:
        logger.error(f'[SocketIO] Error in handle_esp32_frame: {str(e)}')
        socketio.emit('error', {'message': 'Frame processing error'}, room=request.sid)

def cleanup_stale_connections():
    now = datetime.datetime.now()
    stale_sids = []
    for sid, conn in active_connections.items():
        if (now - conn['last_activity']).total_seconds() > 30:
            stale_sids.append(sid)
    for sid in stale_sids:
        conn = active_connections[sid]
        logger.warning(f'[SocketIO] Cleaning up stale connection: {conn["cart_id"]} ({conn["type"]})')
        cart_id = conn['cart_id']
        cart_connections[cart_id].discard(sid)
        if not cart_connections[cart_id]:
            del cart_connections[cart_id]
            if cart_id in frame_buffers:
                del frame_buffers[cart_id]
        del active_connections[sid]

def cleanup_task():
    while True:
        cleanup_stale_connections()
        eventlet.sleep(10)


@socketio.on('authenticate')
def handle_authenticate(data):
    cart_id = data.get('cart_id')
    if not cart_id:
        emit('authentication_failed', {'reason': 'No cart_id provided'})
        return
    emit('connection_confirmed', {
        'status': 'connected',
        'cart_id': cart_id,
        'client_type': 'esp32'
    }, room=request.sid)
    logger.info(f'[SocketIO] Sent connection_confirmed to ESP32 cart {cart_id}')



if __name__ == '__main__':
    try:
        port = get_available_port()
        logger.info(f'[Flask] Starting Flask-SocketIO server with eventlet on port {port}...')
        eventlet.spawn(cleanup_task)
        socketio.run(
            app,
            debug=True,
            host='0.0.0.0',
            port=port,
            use_reloader=False
        )
    except Exception as e:
        logger.error(f'[Flask] Server error: {str(e)}')
