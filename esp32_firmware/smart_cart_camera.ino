#include <WiFi.h>
#include <esp_camera.h>
#include <WebSocketsClient.h>
#include <base64.h>
#include <ArduinoJson.h>

// WiFi credentials
// const char* ssid = "Preetham.V";
// const char* password = "dkzn7849";
const char* ssid = "moto";
const char* password = "12345679";
// Server configuration
const char* server_ip = "192.168.228.77"; // <-- your PC's IP
const int server_port = 5000;             // <-- port for server.py
// const char* server_path = "/";            // <-- plain WebSocket
const char* server_path = "/socket.io/?EIO=4&transport=websocket";
// Cart configuration
const char* cart_id = "cart_001";
unsigned long lastSend = 0;
unsigned long interval = 1000; // 1 second

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
  config.frame_size = FRAMESIZE_VGA;
  config.jpeg_quality = 10;
  config.fb_count = 1;

  esp_err_t err = esp_camera_init(&config);
  if (err != ESP_OK) {
    Serial.printf("Camera init failed with error 0x%x\n", err);
    return;
  }

  pinMode(FLASH_GPIO_NUM, OUTPUT);
  digitalWrite(FLASH_GPIO_NUM, LOW);
}

void toggleFlash(bool enable) {
  flashEnabled = enable;
  digitalWrite(FLASH_GPIO_NUM, enable ? HIGH : LOW);
}

void sendImage() {
  if (!webSocket.isConnected()) {
    Serial.println("WebSocket not connected");
    return;
  }

  camera_fb_t *fb = esp_camera_fb_get();
  if (!fb) {
    Serial.println("Camera capture failed");
    return;
  }

  JsonDocument doc;
  doc["type"] = "esp32_frame";
  doc["cart_id"] = cart_id;
  String imageBase64 = base64::encode(fb->buf, fb->len);
  doc["image"] = imageBase64;

  String jsonString;
  serializeJson(doc, jsonString);

  Serial.println("Sending image frame...");
  webSocket.sendTXT(jsonString);

  esp_camera_fb_return(fb);
}

void sendCartConnectMessage() {
  JsonDocument doc;
  doc["type"] = "cart_connect";
  doc["cart_id"] = cart_id;
  String jsonString;
  serializeJson(doc, jsonString);
  webSocket.sendTXT(jsonString);
}

void handleWebSocketEvent(WStype_t type, uint8_t * payload, size_t length) {
  switch(type) {
    case WStype_DISCONNECTED:
      Serial.println("Disconnected from server");
      break;
    case WStype_CONNECTED:
      Serial.println("Connected to server");
      sendCartConnectMessage();
      break;
    case WStype_TEXT: {
      String message = String((char*)payload);
      if (message.indexOf("flash_on") >= 0) {
        toggleFlash(true);
      } else if (message.indexOf("flash_off") >= 0) {
        toggleFlash(false);
      }
      break;
    }
    default:
      break;
  }
}

void setup() {
  Serial.begin(115200);
  startCamera();

  WiFi.begin(ssid, password);
  Serial.print("Connecting to WiFi");
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("\nConnected to WiFi");
  Serial.print("IP Address: ");
  Serial.println(WiFi.localIP());

  webSocket.begin(server_ip, server_port, server_path);
  webSocket.onEvent(handleWebSocketEvent);
  webSocket.setReconnectInterval(5000);
  webSocket.enableHeartbeat(15000, 3000, 2);
}

void loop() {
  webSocket.loop();

  if (millis() - lastSend > interval && webSocket.isConnected()) {
    sendImage();
    lastSend = millis();
  }

  if (WiFi.status() != WL_CONNECTED) {
    Serial.println("WiFi disconnected. Reconnecting...");
    WiFi.begin(ssid, password);
  }
}