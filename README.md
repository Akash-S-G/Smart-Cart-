# Smart Cart AI

An IoT-based smart shopping cart using ESP32-CAM, HX711 load cell, and a Flask AI backend.

## Table of Contents
- [Features](#features)
- [Hardware Required](#hardware-required)
- [Getting Started](#getting-started)
- [Usage](#usage)
- [Folder Structure](#folder-structure)
- [Contributing](#contributing)
- [License](#license)

## Features
- Real-time product recognition with AI
- Weight measurement and price calculation
- Simple web interface for backend testing

## Hardware Required
- ESP32-CAM
- HX711 + 10kg load cell
- FTDI programmer
- Power supply

## Getting Started

### 1. Clone the repo
git clone https://github.com/Akash-S-G/smart-cart.git

### 2. Flash ESP32-CAM
See [firmware/README.md](firmware/README.md) for instructions.

### 3. Set up backend
cd backend
pip install -r requirements.txt
python server.py

### 4. Test with web interface
Open [http://localhost:5000](http://localhost:5000) in your browser.

## Folder Structure
- `firmware/`: ESP32-CAM code
- `backend/`: Flask server and AI model
- `model/`: Trained model files
- `docs/`: Diagrams and documentation

## License
MIT
