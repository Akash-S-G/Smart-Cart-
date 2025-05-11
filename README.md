# Smart Cart AI

An intelligent shopping cart system using ESP32-CAM, weight sensors, and AI for automatic product recognition and pricing.

---

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Architecture](#architecture)
- [Hardware Requirements](#hardware-requirements)
- [Software Requirements](#software-requirements)
- [Repository Structure](#repository-structure)
- [Installation & Setup](#installation--setup)
- [Usage](#usage)
- [Server Configuration](#server-configuration)
- [ESP32-CAM Configuration](#esp32-cam-configuration)
- [Deployment Options](#deployment-options)
- [API Reference](#api-reference)
- [Security Considerations](#security-considerations)
- [Future Improvements](#future-improvements)
- [Contributing](#contributing)
- [License](#license)

---

## Overview

Smart Cart AI is an IoT project that combines computer vision and weight sensors to create an intelligent shopping cart. The system automatically recognizes products placed in the cart, measures their weight, and calculates the total price.

---

## Features

- Real-time product recognition using deep learning
- Weight-based product detection
- Automatic price calculation
- Web interface for testing and monitoring
- RESTful API for system integration

---

## Architecture

ESP32-CAM + Weight Sensor → WiFi → Backend Server → AI Model → Response


---

## Hardware Requirements

- ESP32-CAM AI-Thinker module
- HX711 load cell amplifier
- 10kg load cell/weight sensor
- FTDI programmer for ESP32-CAM
- Power supply (5V)

---

## Software Requirements

- Python 3.8+
- TensorFlow 2.x
- Flask
- OpenCV
- Arduino IDE (for ESP32-CAM programming)

---

## Repository Structure

smart-cart/
├── firmware/ # ESP32-CAM code
│ ├── esp32-cam-smartcart.ino # Main ESP32-CAM firmware
│ └── README.md # Hardware setup instructions
├── backend/ # Server-side code
│ ├── server.py # Flask API server
│ ├── product_model.py # Model wrapper
│ ├── product_model.h5 # Trained model
│ ├── class_indices.json # Class mapping
│ ├── requirements.txt # Python dependencies
│ └── templates/ # HTML templates
│ └── index.html # Web interface
├── model/ # Model training code
│ └── model_training.ipynb # Training notebook
├── docs/ # Documentation
│ ├── wiring_diagram.png # Hardware wiring diagram
│ ├── api_reference.md # API documentation
│ └── screenshots/ # UI screenshots
└── test_images/ # Sample images for testing


---

## Installation & Setup

### Backend Server
Clone repository
git clone https://github.com/Akash-S-G/smart-cart.git
cd smart-cart/backend

Create virtual environment
python -m venv venv
source venv/bin/activate # Windows: venv\Scripts\activate

Install dependencies
pip install -r requirements.txt

Run server
python server.py


### ESP32-CAM Firmware

1. Install Arduino IDE and ESP32 board support
2. Open `firmware/esp32-cam-smartcart.ino`
3. Configure WiFi settings and server IP address
4. Connect ESP32-CAM via FTDI programmer:
   - GND → GND
   - 5V → 5V
   - U0R → TX
   - U0T → RX
   - GPIO0 → GND (during programming)
5. Upload the code
6. Disconnect GPIO0 from GND and reset the board

---

## Usage

### Web Interface

1. Start the backend server
2. Open a web browser and navigate to `http://localhost:5000`
3. Upload an image and enter a weight
4. View the AI prediction, confidence score, and calculated price

### ESP32-CAM Integration

1. Connect the weight sensor to ESP32-CAM
2. Place the ESP32-CAM where it can view products
3. When a new item is placed on the weight sensor, the ESP32-CAM will:
   - Detect the weight change
   - Capture an image
   - Send both to the backend server
   - Receive product identification and pricing

---

## Server Configuration

### Connecting ESP32-CAM to Local Server

- Find your computer's local IP address:
  - Windows: Run `ipconfig` in Command Prompt
  - Mac/Linux: Run `ifconfig` or `ip addr` in Terminal
- Update the ESP32-CAM code with your computer's IP address:


const char* serverURL = "http://192.168.1.x:5000/api/process"; // Replace with your IP

- Make sure your firewall allows incoming connections on port 5000.

### Exposing Local Server to Internet (Development)

- Install ngrok: https://ngrok.com/download
- Run: `ngrok http 5000`
- Use the provided URL in your ESP32-CAM code:


const char* serverURL = "https://abcd1234.ngrok.io/api/process"; // Your ngrok URL


### Production Deployment

- Host your Flask app on a cloud service (AWS, Google Cloud, Azure, Heroku, etc.)
- Configure a domain name with HTTPS
- Update ESP32-CAM with your public URL:
- 
const char* serverURL = "https://your-domain.com/api/process";

---

## Deployment Options

### Local Development

- Server runs on laptop
- ESP32-CAM connects to local network
- Both devices must be on same WiFi
- Use local IP address (e.g., 192.168.1.x:5000)

### Cloud Deployment

- Host Flask app on cloud platform
- Set up with domain name and HTTPS
- ESP32-CAM sends requests to public URL
- Consider authentication for security

### Hybrid Solution

- Run server on a Raspberry Pi
- Configure port forwarding on router
- Use dynamic DNS service
- Secure with HTTPS and authentication

---

## API Reference

### Main Endpoint: `/api/process`

- Method: POST
- Content-Type: image/jpeg
- Headers:
- X-Weight: weight in grams
- Response:
{
"product": "apple",
"confidence": 0.95,
"weight": 150,
"price": 0.38
}


---

## Security Considerations

- Use HTTPS for all communication
- Implement authentication for API endpoints
- Keep firmware updated
- Consider data privacy regulations

---

## Future Improvements

- Mobile app integration
- Multiple camera support
- Shopping list functionality
- Inventory management
- Payment integration

---

## Contributing

Contributions welcome! Please feel free to submit a Pull Request.

---

## License

This project is licensed under the MIT License.

