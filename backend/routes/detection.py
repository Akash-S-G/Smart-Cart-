from flask import Blueprint, request, jsonify, Response
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import Camera, Detection, AIModel, db
import cv2
import numpy as np
import tensorflow as tf
import json
from datetime import datetime
import os
from app import socketio

detection_bp = Blueprint('detection', __name__)

# Global variables for model and camera streams
model = None
model_classes = []
camera_streams = {}

def load_active_model():
    """Load the currently active AI model"""
    global model, model_classes
    active_model = AIModel.query.filter_by(is_active=True).first()
    if active_model and os.path.exists(active_model.file_path):
        model = tf.keras.models.load_model(active_model.file_path)
        model_classes = json.loads(active_model.classes)
        return True
    return False

def process_frame(frame, camera_id):
    """Process a frame through the AI model"""
    global model, model_classes
    
    if model is None:
        if not load_active_model():
            return None
    
    # Preprocess the frame
    processed_frame = cv2.resize(frame, (224, 224))  # Adjust size based on your model
    processed_frame = processed_frame / 255.0  # Normalize
    processed_frame = np.expand_dims(processed_frame, axis=0)
    
    # Run inference
    predictions = model.predict(processed_frame)
    class_idx = np.argmax(predictions[0])
    confidence = float(predictions[0][class_idx])
    
    if confidence > 0.5:  # Confidence threshold
        product_name = model_classes[class_idx]
        
        # Save detection to database
        detection = Detection(
            camera_id=camera_id,
            product_name=product_name,
            confidence_score=confidence,
            timestamp=datetime.utcnow()
        )
        db.session.add(detection)
        db.session.commit()
        
        # Emit detection via WebSocket
        socketio.emit('detection', {
            'camera_id': camera_id,
            'product_name': product_name,
            'confidence': confidence,
            'timestamp': detection.timestamp.isoformat()
        })
        
        return {
            'product_name': product_name,
            'confidence': confidence
        }
    
    return None

def generate_frames(camera_id):
    """Generate frames for MJPEG stream"""
    camera = Camera.query.get(camera_id)
    if not camera:
        return
    
    # Initialize video capture
    cap = cv2.VideoCapture(f'http://{camera.ip_address}/video')
    
    while True:
        success, frame = cap.read()
        if not success:
            break
        
        # Process frame for detection
        detection = process_frame(frame, camera_id)
        
        # Draw detection results on frame if available
        if detection:
            text = f"{detection['product_name']}: {detection['confidence']:.2f}"
            cv2.putText(frame, text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        
        # Encode frame to JPEG
        ret, buffer = cv2.imencode('.jpg', frame)
        if not ret:
            continue
        
        # Yield frame for streaming
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')

@detection_bp.route('/video_feed/<int:camera_id>')
@jwt_required()
def video_feed(camera_id):
    """Endpoint for streaming video feed"""
    camera = Camera.query.get(camera_id)
    if not camera:
        return jsonify({'error': 'Camera not found'}), 404
    
    return Response(
        generate_frames(camera_id),
        mimetype='multipart/x-mixed-replace; boundary=frame'
    )

@detection_bp.route('/detect', methods=['POST'])
def detect():
    """Endpoint for receiving frames from ESP32-CAM"""
    if 'image' not in request.files:
        return jsonify({'error': 'No image provided'}), 400
    
    camera_id = request.form.get('camera_id')
    if not camera_id:
        return jsonify({'error': 'No camera_id provided'}), 400
    
    # Read and process the image
    file = request.files['image']
    nparr = np.frombuffer(file.read(), np.uint8)
    frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    
    # Process the frame
    result = process_frame(frame, int(camera_id))
    
    if result:
        return jsonify(result), 200
    return jsonify({'message': 'No detection above threshold'}), 200

@detection_bp.route('/recent', methods=['GET'])
@jwt_required()
def get_recent_detections():
    """Get recent detections for a camera"""
    camera_id = request.args.get('camera_id')
    limit = min(int(request.args.get('limit', 10)), 50)  # Max 50 results
    
    query = Detection.query.order_by(Detection.timestamp.desc())
    if camera_id:
        query = query.filter_by(camera_id=camera_id)
    
    detections = query.limit(limit).all()
    
    return jsonify([{
        'id': d.id,
        'camera_id': d.camera_id,
        'product_name': d.product_name,
        'confidence_score': d.confidence_score,
        'timestamp': d.timestamp.isoformat()
    } for d in detections]), 200 