#include <Arduino.h>
#include <Wire.h>
#include <Adafruit_GFX.h>
#include <Adafruit_SSD1306.h>
#include "display.h"
#include "storage.h"

#define SCREEN_WIDTH  128
#define SCREEN_HEIGHT 64
#define ITEM_HEIGHT   16
#define VISIBLE_ITEMS 3

Adafruit_SSD1306 display(SCREEN_WIDTH, SCREEN_HEIGHT, &Wire, -1);

void initDisplay() {
  display.begin(SSD1306_SWITCHCAPVCC, 0x3C);
  display.clearDisplay();
  display.setTextSize(1);

  // Splash
  display.setTextColor(WHITE);
  display.setCursor(28, 20);
  display.print("DevPad v1.0");
  display.setCursor(22, 36);
  display.print("Loading...");
  display.display();
  delay(1200);
}

void drawMenu(int selected) {
  display.clearDisplay();

  int count = getProfileCount();

  // ── Title bar ──────────────────────────────
  display.fillRect(0, 0, 128, 10, WHITE);
  display.setTextColor(BLACK);
  display.setCursor(2, 1);
  display.print("DevPad");

  // Profile index indicator e.g. "2/5"
  String indicator = String(selected + 1) + "/" + String(count);
  display.setCursor(128 - (indicator.length() * 6) - 2, 1);
  display.print(indicator);

  // ── Scrolling window ───────────────────────
  // Calculate scroll offset so selected item is always visible
  int scrollOffset = 0;
  if (selected >= VISIBLE_ITEMS) {
    scrollOffset = selected - VISIBLE_ITEMS + 1;
  }

  display.setTextColor(WHITE);

  for (int i = 0; i < VISIBLE_ITEMS; i++) {
    int profileIndex = i + scrollOffset;
    if (profileIndex >= count) break;

    int y = 11 + i * ITEM_HEIGHT;  // start below title bar

    if (profileIndex == selected) {
      // Highlight selected row
      display.fillRect(0, y, 128, ITEM_HEIGHT, WHITE);
      display.setTextColor(BLACK);
    } else {
      display.setTextColor(WHITE);
    }

    display.setCursor(4, y + 4);
    display.print(profileIndex == selected ? "> " : "  ");
    display.print(getProfileName(profileIndex));
  }

  // ── Scroll arrows ──────────────────────────
  // Up arrow if not at top
  if (scrollOffset > 0) {
    display.setTextColor(WHITE);
    display.setCursor(120, 11);
    display.print("^");
  }

  // Down arrow if more items below
  if (scrollOffset + VISIBLE_ITEMS < count) {
    display.setTextColor(WHITE);
    display.setCursor(120, 54);
    display.print("v");
  }

  display.display();
}

void drawNoProfiles() {
  display.clearDisplay();
  display.setTextColor(WHITE);
  display.setCursor(10, 20);
  display.print("No profiles found.");
  display.setCursor(10, 36);
  display.print("Use DevPad app.");
  display.display();
}

void drawRunning(String name) {
  display.clearDisplay();
  display.setTextColor(WHITE);
  display.setCursor(20, 10);
  display.print("Running:");
  display.setCursor(4, 26);

  // Truncate name if too long for screen
  if (name.length() > 18) name = name.substring(0, 17) + "~";
  display.print(name);

  display.setCursor(24, 46);
  display.print("Please wait...");
  display.display();
}

void drawBLEDisconnected() {
  display.clearDisplay();
  display.setTextColor(WHITE);
  display.setCursor(10, 18);
  display.print("BLE not connected!");
  display.setCursor(8, 34);
  display.print("Pair DevPad first.");
  display.display();
}