#include <WiFi.h>
#include <esp_camera.h>
#include <WebSocketsClient.h>
#include <ArduinoJson.h>
#include <base64.h>

// Replace with your Wi-Fi credentials
const char* ssid = "Preetham .V";
const char* password = "dkzn7849";

// Flask server settings
const char* server_ip = "192.168.8.77";
const int server_port = 5000;
const char* server_path = "/socket.io/?EIO=4&transport=websocket";

// Smart Cart settings
const String CART_ID = "CART_001"; // Unique ID for this cart
unsigned long lastSend = 0;
unsigned long interval = 1000; // Send frame every 1 second
bool isConnected = false;

WebSocketsClient webSocket;

// Camera pins for AI Thinker ESP32-CAM board
#define PWDN_GPIO_NUM     32
#define RESET_GPIO_NUM    -1
#define XCLK_GPIO_NUM      0
#define SIOD_GPIO_NUM     26
#define SIOC_GPIO_NUM     27
#define Y9_GPIO_NUM       35
#define Y8_GPIO_NUM       34
#define Y7_GPIO_NUM       39
#define Y6_GPIO_NUM       36
#define Y5_GPIO_NUM       21
#define Y4_GPIO_NUM       19
#define Y3_GPIO_NUM       18
#define Y2_GPIO_NUM        5
#define VSYNC_GPIO_NUM    25
#define HREF_GPIO_NUM     23
#define PCLK_GPIO_NUM     22

// LED Flash control
#define FLASH_GPIO_NUM 4
bool flashEnabled = false;

void startCamera() {
    camera_config_t config;
    config.ledc_channel = LEDC_CHANNEL_0;
    config.ledc_timer = LEDC_TIMER_0;
    config.pin_d0 = Y2_GPIO_NUM;
    config.pin_d1 = Y3_GPIO_NUM;
    config.pin_d2 = Y4_GPIO_NUM;
    config.pin_d3 = Y5_GPIO_NUM;
    config.pin_d4 = Y6_GPIO_NUM;
    config.pin_d5 = Y7_GPIO_NUM;
    config.pin_d6 = Y8_GPIO_NUM;
    config.pin_d7 = Y9_GPIO_NUM;
    config.pin_xclk = XCLK_GPIO_NUM;
    config.pin_pclk = PCLK_GPIO_NUM;
    config.pin_vsync = VSYNC_GPIO_NUM;
    config.pin_href = HREF_GPIO_NUM;
    config.pin_sccb_sda = SIOD_GPIO_NUM;
    config.pin_sccb_scl = SIOC_GPIO_NUM;
    config.pin_pwdn = PWDN_GPIO_NUM;
    config.pin_reset = RESET_GPIO_NUM;
    config.xclk_freq_hz = 20000000;
    config.pixel_format = PIXFORMAT_JPEG;
    
    // Set initial frame size
    config.frame_size = FRAMESIZE_VGA; // 640x480
    config.jpeg_quality = 10; // Lower value = higher quality (0-63)
    config.fb_count = 2; // Number of frame buffers

    // Initialize camera
    esp_err_t err = esp_camera_init(&config);
    if (err != ESP_OK) {
        Serial.printf("Camera init failed with error 0x%x", err);
        return;
    }

    // Configure flash LED
    pinMode(FLASH_GPIO_NUM, OUTPUT);
    digitalWrite(FLASH_GPIO_NUM, LOW); // Turn off flash initially
}

void toggleFlash(bool enable) {
    digitalWrite(FLASH_GPIO_NUM, enable ? HIGH : LOW);
    flashEnabled = enable;
}

void sendImage() {
    // Enable flash for better image quality
    toggleFlash(true);
    delay(100); // Brief delay for flash to take effect

    camera_fb_t *fb = esp_camera_fb_get();
    if (!fb) {
        Serial.println("Camera capture failed");
        toggleFlash(false);
        return;
    }

    // Create JSON document
    JsonDocument doc;
    doc["type"] = "esp32_frame";
    doc["cart_id"] = CART_ID;
    
    // Convert image to base64
    String imageBase64 = base64::encode(fb->buf, fb->len);
    doc["image"] = imageBase64;

    // Serialize JSON to string
    String jsonString;
    serializeJson(doc, jsonString);

    // Send to server
    webSocket.sendTXT(jsonString);

    // Clean up
    esp_camera_fb_return(fb);
    toggleFlash(false);
}

void handleCartUpdate(uint8_t *payload) {
    JsonDocument doc;
    DeserializationError error = deserializeJson(doc, payload);
    
    if (error) {
        Serial.println("JSON parsing failed");
        return;
    }

    // Handle cart updates
    if (doc["cart_updated"].is<bool>() && doc["cart_updated"].as<bool>()) {
        // Product detected and added to cart
        const char* productName = doc["detections"][0]["product_name"];
        float confidence = doc["detections"][0]["confidence"];
        
        // Visual feedback - flash LED twice
        toggleFlash(true);
        delay(100);
        toggleFlash(false);
        delay(100);
        toggleFlash(true);
        delay(100);
        toggleFlash(false);
        
        Serial.printf("Product detected: %s (%.2f%%)\n", productName, confidence * 100);
    }
}

void sendCartConnectMessage() {
    JsonDocument doc;
    doc["type"] = "cart_connect";
    doc["cart_id"] = CART_ID;
    
    String jsonString;
    serializeJson(doc, jsonString);
    webSocket.sendTXT(jsonString);
}

void webSocketEvent(WStype_t type, uint8_t *payload, size_t length) {
    switch (type) {
        case WStype_DISCONNECTED:
            Serial.println("Disconnected from server");
            isConnected = false;
            break;
            
        case WStype_CONNECTED:
            Serial.println("Connected to server");
            isConnected = true;
            sendCartConnectMessage();
            break;
            
        case WStype_TEXT:
            handleCartUpdate(payload);
            break;
            
        case WStype_ERROR:
            Serial.println("WebSocket Error");
            break;
    }
}

void setup() {
    Serial.begin(115200);
    
    // Initialize camera
    startCamera();
    
    // Connect to WiFi
    WiFi.begin(ssid, password);
    Serial.print("Connecting to WiFi");
    
    while (WiFi.status() != WL_CONNECTED) {
        delay(500);
        Serial.print(".");
    }
    
    Serial.println("\nConnected to WiFi");
    Serial.print("IP Address: ");
    Serial.println(WiFi.localIP());

    // Configure WebSocket
    webSocket.begin(server_ip, server_port, server_path);
    webSocket.onEvent(webSocketEvent);
    webSocket.setReconnectInterval(5000);
    
    // Flash LED to indicate setup complete
    toggleFlash(true);
    delay(500);
    toggleFlash(false);
}

void loop() {
    webSocket.loop();

    // Send image if connected and interval has passed
    if (isConnected && (millis() - lastSend > interval)) {
        sendImage();
        lastSend = millis();
    }

    // If disconnected, try to reconnect to WiFi
    if (WiFi.status() != WL_CONNECTED) {
        Serial.println("WiFi connection lost. Reconnecting...");
        WiFi.begin(ssid, password);
        delay(5000);
    }
} 