#include <Arduino.h>
#include "menu.h"
#include "buttons.h"
#include "display.h"
#include "ble_keyboard.h"
#include "storage.h" 

int current = 0;

void updateMenu() {

  if (isNextPressed()) {
    current = (current + 1) % getProfileCount();
  }

  if (isSelectPressed()) {
    runProfile(current);
  }

  drawMenu(current);
}