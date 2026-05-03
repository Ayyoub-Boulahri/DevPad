#include <Arduino.h>
#include <SPIFFS.h>
#include <ArduinoJson.h>
#include "storage.h"
#include "ble_keyboard.h"
#include "leds.h"

#define MAX_PROFILES 10

String profileNames[MAX_PROFILES];
DynamicJsonDocument doc(4096);

int profileCount = 0;

void initStorage()
{
  SPIFFS.begin(true);
  loadProfiles();
}

void loadProfiles()
{
  File file = SPIFFS.open("/config.json", "r");

  if (!file)
  {
    return;
  }

  DeserializationError error = deserializeJson(doc, file);

  if (error)
  {
    Serial.print("❌ JSON parse failed: ");
    return;
  }

  if (!doc.containsKey("profiles"))
  {
    return;
  }

  JsonArray profiles = doc["profiles"];

  profileCount = 0;

  for (JsonObject p : profiles)
  {

    String name = p["name"] | "UNKNOWN";

    profileNames[profileCount] = name;
    profileCount++;

    Serial.print("Loaded profile: ");
  }

  Serial.print("TOTAL PROFILES: ");
}

int getProfileCount()
{
  return profileCount;
}

String getProfileName(int index)
{
  return profileNames[index];
}

void runProfile(int index)
{
  JsonArray profiles = doc["profiles"];
  JsonObject profile = profiles[index];

  JsonArray actions = profile["actions"];

  setYellowLED(true);
  setGreenLED(false);

  for (JsonObject action : actions)
  {
    String type = action["type"];

    if (type == "keys")
    {
      sendOpenTerminal();
    }

    if (type == "text")
    {
      String text = action["data"];
      sendText(text.c_str());
    }

    delay(300);
  }

  setYellowLED(false);
  setGreenLED(true);
}

bool deleteProfile(int index)
{
  if (index < 0 || index >= profileCount)
    return false;

  JsonArray profiles = doc["profiles"];

  // Rebuild array without the deleted index
  DynamicJsonDocument newDoc(8192);
  JsonArray newProfiles = newDoc.createNestedArray("profiles");

  int i = 0;
  for (JsonObject p : profiles)
  {
    if (i != index)
    {
      newProfiles.add(p);
    }
    i++;
  }

  doc.set(newDoc);
  saveProfiles();
  loadProfiles();
  return true;
}

// ── Save to SPIFFS ───────────────────────────
void saveProfiles()
{
  File file = SPIFFS.open(CONFIG_PATH, "w");
  if (!file)
  {
    return;
  }
  serializeJsonPretty(doc, file);
  file.close();
}