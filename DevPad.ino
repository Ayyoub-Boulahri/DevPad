#include "display.h"
#include "buttons.h"
#include "ble_keyboard.h"
#include "menu.h"
#include "storage.h"
#include "leds.h"
#include "serial_api.h"

void setup() {
  initDisplay();
  initButtons();
  initStorage();
  initLEDs();
  initBLE();
  initSerialAPI();
}

void loop() {
  updateSerialAPI();
  updateButtons();
  updateMenu();
}