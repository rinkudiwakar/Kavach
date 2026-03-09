#!/usr/bin/env python3
"""
Raspberry Pi Gateway Server
Receives backend decision JSON via HTTP POST
and controls Arduino accordingly.
"""

from flask import Flask, request, jsonify
import serial
import time

# ---------------- Configuration ----------------
ARDUINO_PORT = '/dev/ttyUSB0'   # Use: ls /dev/tty* to confirm
BAUD_RATE = 9600
PI_HOST = '0.0.0.0'
PI_PORT = 5001
# ------------------------------------------------

app = Flask(__name__)

# Initialize Arduino serial connection
try:
    arduino = serial.Serial(ARDUINO_PORT, BAUD_RATE, timeout=1)
    time.sleep(2)
    print(f"✅ Connected to Arduino on {ARDUINO_PORT}")
except Exception as e:
    print(f"❌ Could not connect to Arduino: {e}")
    arduino = None


def send_command_to_arduino(command):
    """Send a string command to Arduino via serial."""
    try:
        if arduino:
            arduino.write(f"{command}\n".encode())
            print(f"📤 Sent to Arduino: {command}")
        else:
            print("⚠️ Arduino not connected.")
    except Exception as e:
        print(f"❌ Error sending command to Arduino: {e}")


@app.route("/door", methods=["POST"])
def control_door():
    """
    Expected JSON format:
    {
        "decision": "accepted" or "rejected",
        "best_match": {...},      # optional
        "keyword_present": true   # optional
    }
    """
    try:
        data = request.get_json(force=True)
        print(f"\n📩 Received from client: {data}")

        decision = data.get("decision", "").lower()

        # Map backend decision to Arduino command
        if decision == "accepted":
            send_command_to_arduino("OPEN_DOOR")
            return jsonify({"status": "success", "message": "Door opened"}), 200

        elif decision == "rejected":
            send_command_to_arduino("ACCESS_DENIED")
            return jsonify({"status": "success", "message": "Access denied"}), 200

        else:
            send_command_to_arduino("INVALID")
            return jsonify({"status": "error", "message": "Unknown decision"}), 400

    except Exception as e:
        print(f"❌ Error processing request: {e}")
        return jsonify({"status": "error", "message": "Internal Server Error"}), 500


@app.route("/", methods=["GET"])
def home():
    return "🚀 Raspberry Pi Gateway is running!", 200


if __name__ == "__main__":
    print(f"🌐 Starting Raspberry Pi Gateway on port {PI_PORT}...")
