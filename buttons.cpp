#include <Arduino.h>
#include "buttons.h"

#define BTN_NEXT 5
#define BTN_SELECT 18

bool nextPressed = false;
bool selectPressed = false;

void initButtons() {
  pinMode(BTN_NEXT, INPUT_PULLUP);
  pinMode(BTN_SELECT, INPUT_PULLUP);
}

void updateButtons() {
  nextPressed = false;
  selectPressed = false;

  if (digitalRead(BTN_NEXT) == LOW) {
    nextPressed = true;
    delay(200);
  }

  if (digitalRead(BTN_SELECT) == LOW) {
    selectPressed = true;
    delay(200);
  }
}

bool isNextPressed() {
  return nextPressed;
}

bool isSelectPressed() {
  return selectPressed;
}