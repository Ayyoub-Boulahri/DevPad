
import serial
import serial.tools.list_ports
import json
import time

class SerialManager:
    def __init__(self):
        self.ser = None
        self.port = None

    def list_ports(self):
        return [p.device for p in serial.tools.list_ports.comports()]

    def connect(self, port: str, baud=115200) -> bool:
        try:
            self.ser = serial.Serial(port, baud, timeout=3)
            self.port = port
            time.sleep(2)  # wait for ESP32 to reset
            return True
        except Exception as e:
            print(f"Serial connect error: {e}")
            return False

    def disconnect(self):
        if self.ser and self.ser.is_open:
            self.ser.close()
        self.ser = None

    def is_connected(self) -> bool:
        return self.ser is not None and self.ser.is_open

    def send_command(self, cmd: dict) -> dict | None:
        if not self.is_connected():
            return None
        try:
            # Clear any pending data in the buffer first
            self.ser.reset_input_buffer()
            
            raw = json.dumps(cmd) + "\n"
            self.ser.write(raw.encode())
            self.ser.flush()

            # Read lines until we get a valid JSON response
            for _ in range(30):  # max 30 lines
                line = self.ser.readline().decode(errors='ignore').strip()
                if not line:
                    continue
                print(f"[ESP32] {line}")  # helpful for debugging
                try:
                    return json.loads(line)
                except json.JSONDecodeError:
                    continue  # skip debug lines, keep reading

        except Exception as e:
            print(f"Serial error: {e}")
        return None

    def get_profiles(self) -> dict | None:
        return self.send_command({"cmd": "get"})

    def save_profiles(self, data: dict) -> dict | None:
        return self.send_command({"cmd": "save", "data": data})