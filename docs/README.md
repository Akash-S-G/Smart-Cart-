# Smart Cart AI Web System

A full-featured, responsive, and real-time web application that integrates ESP32-CAM for product detection using AI, with admin and user dashboards, and store locator functionality.

## Features

- Live video streaming from ESP32-CAM
- Real-time AI product detection
- Admin dashboard for system management
- User dashboard for product tracking
- Store locator with map integration
- Responsive design for all devices

## Tech Stack

- **Frontend**: React.js with Tailwind CSS
- **Backend**: Flask (Python)
- **AI Model**: TensorFlow/Keras
- **Database**: SQLite
- **Maps**: Leaflet.js with OpenStreetMap
- **Real-time Updates**: WebSocket
- **Video Stream**: MJPEG

## Project Structure

```
project-root/
├── backend/             # Flask server
│   ├── routes/         # API endpoints
│   ├── models/         # Database models
│   └── utils/          # Helper functions
├── frontend/           # React application
│   ├── src/
│   ├── public/
│   └── package.json
├── model/              # AI model files
├── esp32_firmware/     # ESP32-CAM code
└── docker/             # Docker configuration
```

## Setup Instructions

### Prerequisites

- Python 3.8+
- Node.js 14+
- ESP32-CAM
- Docker (optional)

### Backend Setup

1. Create and activate virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your configuration
```

4. Run Flask server:
```bash
python run.py
```

### Frontend Setup

1. Install dependencies:
```bash
cd frontend
npm install
```

2. Start development server:
```bash
npm start
```

### ESP32-CAM Setup

1. Install Arduino IDE
2. Install ESP32 board support
3. Flash the firmware from esp32_firmware/
4. Configure WiFi credentials in the code

## API Documentation

### Main Endpoints

- `POST /api/detect` - Send images for detection
- `GET /api/video_feed` - MJPEG video stream
- `GET /api/predictions` - Get latest predictions
- `POST /api/admin/model` - Upload new model (admin only)

Full API documentation available in `/docs`

## Contributing

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a new Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details. 