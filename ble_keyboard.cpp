#include <Arduino.h>
#include <BleKeyboard.h>
#include "ble_keyboard.h"

BleKeyboard bleKeyboard("DevDeck");

void initBLE() {
  bleKeyboard.begin();
}

void sendOpenTerminal() {
  bleKeyboard.press(KEY_LEFT_CTRL);
  bleKeyboard.press(KEY_LEFT_ALT);
  bleKeyboard.press('t');
  delay(100);
  bleKeyboard.releaseAll();
}

void sendText(const char* text) {
  for (int i = 0; text[i] != '\0'; i++) {
    bleKeyboard.print(text[i]);
    delay(30);   
  }
  delay(500);
  bleKeyboard.write(KEY_RETURN);
}