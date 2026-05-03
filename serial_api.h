#ifndef SERIAL_API_H
#define SERIAL_API_H

#include <ArduinoJson.h>

void initSerialAPI();
void updateSerialAPI();
void sendOk(const String& jsonData = "");
void sendError(const String& message);
void handleGet();
void handleSave(JsonObject& payload);

#endif