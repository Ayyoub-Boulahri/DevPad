#include <Arduino.h>
#include <ArduinoJson.h>
#include <SPIFFS.h>
#include "serial_api.h"
#include "storage.h"

void initSerialAPI() {
  Serial.begin(115200); 
}

// No default arg in the definition (only allowed in declaration)
void sendOk(const String& jsonData) {
  if (jsonData.isEmpty()) {
    Serial.println("{\"status\":\"ok\"}");
  } else {
    Serial.println("{\"status\":\"ok\",\"data\":" + jsonData + "}");
  }
}

void sendError(const String& message) {
  Serial.println("{\"status\":\"error\",\"message\":\"" + message + "\"}");
}

void handleGet() {
  File file = SPIFFS.open("/config.json", "r");
  if (!file) {
    sendError("Cannot open config.json");
    return;
  }

  String content = "";
  while (file.available()) {
    content += (char)file.read();
  }
  file.close();

  content.replace("\n", "");
  content.replace("  ", "");
  sendOk(content);
}

void handleSave(JsonObject& payload) {
  String newConfig;
  serializeJsonPretty(payload, newConfig);

  File file = SPIFFS.open("/config.json", "w");
  if (!file) {
    sendError("Cannot write config.json");
    return;
  }

  file.print(newConfig);
  file.close();

  loadProfiles();
  sendOk(String(""));
  Serial.println("Profiles updated from PC.");
}

void updateSerialAPI() {
  if (!Serial.available()) return;

  String line = Serial.readStringUntil('\n');
  line.trim();
  if (line.isEmpty()) return;

  Serial.print("Received: ");
  Serial.println(line);

  DynamicJsonDocument incoming(8192);
  DeserializationError err = deserializeJson(incoming, line);

  if (err) {
    sendError("JSON parse failed");
    return;
  }

  String cmd = incoming["cmd"] | "";

  if (cmd == "get") {
    handleGet();

  } else if (cmd == "save") {
    if (!incoming.containsKey("data")) {
      sendError("Missing 'data' field");
      return;
    }
    JsonObject data = incoming["data"];
    handleSave(data);

  } else if (cmd == "delete") {
    if (!incoming.containsKey("index")) {
      sendError("Missing 'index' field");
      return;
    }
    int idx = incoming["index"];
    if (deleteProfile(idx)) {
      sendOk(String(""));
    } else {
      sendError("Invalid profile index");
    }

  } else {
    sendError("Unknown command: " + cmd);
  }
}