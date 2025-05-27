#include <WiFi.h>
#include <esp_camera.h>
#include <WebSocketsClient.h>
#include <ArduinoJson.h>
#include <base64.h>

// Replace with your Wi-Fi credentials
const char* ssid = "Preetham .V";
const char* password = "dkzn7849";

// Flask server settings
const char* server_ip = "192.168.175.155"; // Your server IP
const int server_port = 5000; // Changed to Socket.IO port
const char* server_path = "/socket.io/?EIO=4&transport=websocket"; // Socket.IO endpoint

// Smart Cart settings
const String CART_ID = "cart_001"; // Unique ID for this cart
unsigned long lastSend = 0;
unsigned long interval = 1000; // Send frame every 1 second
bool isConnected = false;
unsigned long lastPing = 0;
const unsigned long pingInterval = 25000; // 25 seconds ping interval

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

void handleSocketIOEvent(WStype_t type, uint8_t * payload, size_t length) {
    switch(type) {
        case WStype_DISCONNECTED:
            Serial.println("Disconnected from server");
            isConnected = false;
            break;
            
        case WStype_CONNECTED:
            Serial.println("Connected to server");
            // Send Socket.IO connection upgrade
            webSocket.sendTXT("40");
            break;
            
        case WStype_TEXT:
            Serial.printf("Received text: %s\n", payload);
            // Handle Socket.IO protocol messages
            if (strcmp((char*)payload, "2") == 0) {
                // Ping message, respond with pong
                webSocket.sendTXT("3");
            }
            else if (strncmp((char*)payload, "40", 2) == 0) {
                // Connection confirmed
                isConnected = true;
                // Send authentication with cart ID
                String authMsg = "42[\"connect\",{\"cart_id\":\"" + CART_ID + "\"}]";
                webSocket.sendTXT(authMsg);
            }
            break;
            
        case WStype_ERROR:
            Serial.printf("WebSocket error: %s\n", payload);
            break;
    }
}

void setup() {
    WRITE_PERI_REG(RTC_CNTL_BROWN_OUT_REG, 0);
    
    Serial.begin(115200);
    Serial.println();
    
    // Initialize camera
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
    config.pin_sscb_sda = SIOD_GPIO_NUM;
    config.pin_sscb_scl = SIOC_GPIO_NUM;
    config.pin_pwdn = PWDN_GPIO_NUM;
    config.pin_reset = RESET_GPIO_NUM;
    config.xclk_freq_hz = 20000000;
    config.pixel_format = PIXFORMAT_JPEG;
    config.frame_size = FRAMESIZE_VGA;
    config.jpeg_quality = 12;
    config.fb_count = 2;
    
    // Initialize camera
    esp_err_t err = esp_camera_init(&config);
    if (err != ESP_OK) {
        Serial.printf("Camera init failed with error 0x%x", err);
        return;
    }
    
    // Configure and enable flash
    pinMode(FLASH_GPIO_NUM, OUTPUT);
    digitalWrite(FLASH_GPIO_NUM, 0);
    
    // Connect to WiFi
    WiFi.begin(ssid, password);
    Serial.print("Connecting to WiFi");
    while (WiFi.status() != WL_CONNECTED) {
        delay(500);
        Serial.print(".");
    }
    Serial.println();
    Serial.print("Connected to WiFi, IP address: ");
    Serial.println(WiFi.localIP());
    
    // Configure WebSocket
    webSocket.begin(server_ip, server_port, server_path);
    webSocket.onEvent(handleSocketIOEvent);
    webSocket.setReconnectInterval(5000);
}

void sendImage() {
    camera_fb_t * fb = esp_camera_fb_get();
    if (!fb) {
        Serial.println("Camera capture failed");
        return;
    }
    
    // Create JSON document
    DynamicJsonDocument doc(1024);
    doc["cart_id"] = CART_ID;
    
    // Convert image to base64
    String base64Image = base64::encode(fb->buf, fb->len);
    
    // Split image into chunks if needed
    const int chunkSize = 8192;
    int chunks = (base64Image.length() + chunkSize - 1) / chunkSize;
    
    for (int i = 0; i < chunks; i++) {
        String chunk = base64Image.substring(i * chunkSize, min((i + 1) * chunkSize, (int)base64Image.length()));
        
        doc["chunk"] = chunk;
        doc["final"] = (i == chunks - 1);
        
        String jsonString;
        serializeJson(doc, jsonString);
        
        // Send as Socket.IO message
        String socketMessage = "42[\"esp32_frame\"," + jsonString + "]";
        webSocket.sendTXT(socketMessage);
        
        // Small delay between chunks
        delay(10);
    }
    
    esp_camera_fb_return(fb);
}

void loop() {
    webSocket.loop();
    
    // Send image periodically if connected
    if (isConnected && millis() - lastSend > interval) {
        sendImage();
        lastSend = millis();
    }
    
    // Check WiFi connection
    if (WiFi.status() != WL_CONNECTED) {
        Serial.println("WiFi disconnected. Reconnecting...");
        WiFi.begin(ssid, password);
    }
} 