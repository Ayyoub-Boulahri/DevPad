#include <Arduino.h>
#include "leds.h"

#define YELLOW_LED_PIN 2
#define GREEN_LED_PIN 4

void initLEDs() {
  pinMode(YELLOW_LED_PIN, OUTPUT);
  pinMode(GREEN_LED_PIN, OUTPUT);
}

void setYellowLED(bool state) {
  digitalWrite(YELLOW_LED_PIN, state ? HIGH : LOW);
}

void setGreenLED(bool state) {
  digitalWrite(GREEN_LED_PIN, state ? HIGH : LOW);
}