#ifndef BLE_KEYBOARD_H
#define BLE_KEYBOARD_H

void initBLE();
void sendOpenTerminal();
void sendText(const char* text);

#endif