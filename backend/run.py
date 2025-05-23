from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_socketio import SocketIO
from routes.auth import auth
import datetime

app = Flask(__name__)
CORS(app)

# JWT Configuration
app.config['JWT_SECRET_KEY'] = 'your-secret-key'  # Change this in production!
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = datetime.timedelta(days=1)
jwt = JWTManager(app)

# Initialize Socket.IO
socketio = SocketIO(app, cors_allowed_origins="*")

# Register blueprints
app.register_blueprint(auth, url_prefix='/auth')

@app.route('/')
def hello():
    return {"message": "SmartCart API is running!"}

# Socket.IO event handlers
@socketio.on('connect')
def handle_connect():
    print('Client connected')

@socketio.on('disconnect')
def handle_disconnect():
    print('Client disconnected')

@socketio.on('esp32_frame')
def handle_esp32_frame(data):
    print('Received frame from ESP32:', data.get('cart_id'))
    # Broadcast the frame to all connected clients
    socketio.emit('frame_update', data)

if __name__ == '__main__':
    socketio.run(app, debug=True, host='0.0.0.0', port=5000, allow_unsafe_werkzeug=True) 