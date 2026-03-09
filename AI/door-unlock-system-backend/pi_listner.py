import socket
import serial
import time

# ---------------- Configuration ----------------
HOST = "0.0.0.0"   # Listen on all interfaces
PORT = 5000        # Must match client.py's PI_PORT
SERIAL_PORT = "/dev/ttyACM0"  # Change if your Arduino is on another port
BAUD_RATE = 9600
# ------------------------------------------------

def setup_serial():
    try:
        ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
        time.sleep(2)  # Wait for Arduino to initialize
        print("✅ Connected to Arduino on", SERIAL_PORT)
        return ser
    except Exception as e:
        print("❌ Could not connect to Arduino:", e)
        return None

def listen_for_commands(ser):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, PORT))
        s.listen(1)
        print(f"📡 Raspberry Pi listening on port {PORT}...")

        while True:
            conn, addr = s.accept()
            with conn:
                print(f"\n📥 Connection from {addr}")
                data = conn.recv(1024).decode().strip()
                if not data:
                    continue

                print(f"🧠 Received command: {data}")

                if ser:
                    if data.lower() == "open":
                        ser.write(b"OPEN_DOOR\n")
                    elif data.lower() == "close":
                        ser.write(b"CLOSE_DOOR\n")
                    else:
                        ser.write(b"ACCESS_DENIED\n")

                    print(f"➡️ Sent to Arduino: {data.upper()}")
                    # Optionally, read response back from Arduino
                    time.sleep(0.5)
                    while ser.in_waiting:
                        response = ser.readline().decode().strip()
                        if response:
                            print(f"🔁 Arduino: {response}")
                else:
                    print("⚠️ Serial not connected. Cannot send to Arduino.")

def main():
    ser = setup_serial()
    listen_for_commands(ser)

if __name__ == "__main__":
    main()
