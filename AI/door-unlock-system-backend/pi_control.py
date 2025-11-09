import serial
import time
import logging
from fusion_pipeline import get_intent

# Logging
logging.basicConfig(
    filename="door_access.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

arduino = serial.Serial("/dev/ttyUSB0", 9600, timeout=1)
time.sleep(2)  # wait for Arduino

# Track consecutive failed attempts
failed_attempts = 0

def handle_access():
    global failed_attempts
    try:
        print("🎙️ Recording voice for authentication...")
        result = get_intent(duration=3)
        voice_result = result["voice_auth"]
        intent_result = result["rhino"]
        logging.info(f"Voice auth: {voice_result}, Intent: {intent_result}")

        if voice_result["result"] == "granted" and intent_result["intent"] == "open_door":
            print("✅ Access granted! Opening door...")
            logging.info("Access granted")
            arduino.write(b"OPEN\n")
            failed_attempts = 0  # reset
        else:
            print("❌ Access denied! Closing door...")
            logging.warning("Access denied")
            arduino.write(b"CLOSE\n")
            failed_attempts += 1
            if failed_attempts >= 3:
                trigger_alert()
    except Exception as e:
        logging.error(f"Error during voice authentication: {e}")
        arduino.write(b"CLOSE\n")

def trigger_alert():
    print("🚨 Multiple failed attempts! Alert triggered.")
    logging.warning("🚨 ALERT: Multiple failed attempts!")
    # Send command to Arduino to trigger alert (Arduino handles flashing LEDs & buzzer)
    arduino.write(b"INVALID\n")
    global failed_attempts
    failed_attempts = 0  # reset counter

# Main loop
if __name__ == "__main__":
    print("System ready. Waiting for button press from Arduino...")
    try:
        while True:
            if arduino.in_waiting > 0:
                message = arduino.readline().decode().strip()
                if message == "BUTTON_PRESSED":
                    handle_access()
            time.sleep(0.1)
    except KeyboardInterrupt:
        print("Stopping system...")
        arduino.write(b"CLOSE\n")
