#!/usr/bin/env python3
"""
Raspberry Pi Audio Recording Controller
Listens to Arduino button presses via serial and manages audio recording
"""

import serial
import pyaudio
import wave
import requests
import time
import os
from datetime import datetime

# Configuration
ARDUINO_PORT = '/dev/ttyACM0'  # or /dev/ttyUSB0 - check with: ls /dev/tty*
BAUD_RATE = 9600
BACKEND_API_URL = 'http://localhost:5000/api/process-audio'  # Change to your backend URL

# Audio settings
CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 16000
RECORDINGS_DIR = '/home/pi/recordings'  # Change as needed

class AudioRecorder:
    def __init__(self):
        self.is_recording = False
        self.frames = []
        self.audio = pyaudio.PyAudio()
        self.stream = None
        self.current_filename = None
        
        # Create recordings directory if it doesn't exist
        if not os.path.exists(RECORDINGS_DIR):
            os.makedirs(RECORDINGS_DIR)
    
    def start_recording(self):
        """Start recording audio"""
        if self.is_recording:
            print("Already recording!")
            return
        
        print("🎙️  Starting recording...")
        self.is_recording = True
        self.frames = []
        
        # Generate filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.current_filename = os.path.join(RECORDINGS_DIR, f"recording_{timestamp}.wav")
        
        # Open audio stream
        self.stream = self.audio.open(
            format=FORMAT,
            channels=CHANNELS,
            rate=RATE,
            input=True,
            frames_per_buffer=CHUNK
        )
        
        print(f"Recording to: {self.current_filename}")
    
    def record_chunk(self):
        """Record a chunk of audio (call this in loop while recording)"""
        if self.is_recording and self.stream:
            try:
                data = self.stream.read(CHUNK, exception_on_overflow=False)
                self.frames.append(data)
            except Exception as e:
                print(f"Error recording chunk: {e}")
    
    def stop_recording_and_process(self, arduino):
        """Stop recording, save file, and immediately send to backend"""
        if not self.is_recording:
            print("Not currently recording!")
            return
        
        print("⏹️  Stopping recording...")
        self.is_recording = False
        
        # Close stream
        if self.stream:
            self.stream.stop_stream()
            self.stream.close()
            self.stream = None
        
        # Save WAV file
        if self.frames:
            wf = wave.open(self.current_filename, 'wb')
            wf.setnchannels(CHANNELS)
            wf.setsampwidth(self.audio.get_sample_size(FORMAT))
            wf.setframerate(RATE)
            wf.writeframes(b''.join(self.frames))
            wf.close()
            print(f"✅ Saved: {self.current_filename}")
            
            # Immediately send to backend (no delay)
            print("⚡ Sending to backend immediately...")
            response = self.send_to_backend(self.current_filename)
            
            # Process response right away
            if response:
                handle_backend_response(arduino, response)
            else:
                print("❌ No response from backend")
                send_command_to_arduino(arduino, "ACCESS_DENIED")
    
    def send_to_backend(self, filename):
        """Send audio file to backend API and handle response"""
        if not filename or not os.path.exists(filename):
            print("❌ No file to send!")
            return None
        
        print(f"📤 Sending audio to backend: {BACKEND_API_URL}")
        
        try:
            with open(filename, 'rb') as audio_file:
                files = {'audio': audio_file}
                response = requests.post(BACKEND_API_URL, files=files, timeout=30)
                
                if response.status_code == 200:
                    result = response.json()
                    print(f"✅ Backend response: {result}")
                    return result
                else:
                    print(f"❌ Backend error: {response.status_code} - {response.text}")
                    return None
        
        except requests.exceptions.RequestException as e:
            print(f"❌ Error sending to backend: {e}")
            return None
        except Exception as e:
            print(f"❌ Unexpected error: {e}")
            return None
    
    def cleanup(self):
        """Cleanup audio resources"""
        if self.stream:
            self.stream.stop_stream()
            self.stream.close()
        self.audio.terminate()

def main():
    print("🚀 Starting Arduino Audio Controller...")
    print(f"Connecting to Arduino on {ARDUINO_PORT}...")
    
    # Initialize recorder
    recorder = AudioRecorder()
    
    try:
        # Connect to Arduino
        arduino = serial.Serial(ARDUINO_PORT, BAUD_RATE, timeout=1)
        time.sleep(2)  # Wait for Arduino to initialize
        print("✅ Connected to Arduino!")
        
        while True:
            # Record audio chunks if recording
            if recorder.is_recording:
                recorder.record_chunk()
            
            # Check for Arduino messages
            if arduino.in_waiting > 0:
                line = arduino.readline().decode('utf-8').strip()
                print(f"Arduino: {line}")
                
                if line == "BUTTON_PRESSED":
                    if not recorder.is_recording:
                        # Start recording
                        recorder.start_recording()
                    else:
                        # Stop recording and immediately send to backend
                        recorder.stop_recording_and_process(arduino)
            
            time.sleep(0.01)  # Small delay to prevent CPU overuse
    
    except serial.SerialException as e:
        print(f"❌ Serial connection error: {e}")
        print(f"Make sure Arduino is connected to {ARDUINO_PORT}")
        print("Check available ports with: ls /dev/tty*")
    
    except KeyboardInterrupt:
        print("\n⏹️  Shutting down...")
    
    finally:
        recorder.cleanup()
        if 'arduino' in locals():
            arduino.close()
        print("👋 Goodbye!")

def send_command_to_arduino(arduino, command):
    """Send command to Arduino via serial"""
    try:
        arduino.write(f"{command}\n".encode())
        print(f"📤 Sent to Arduino: {command}")
    except Exception as e:
        print(f"❌ Error sending command to Arduino: {e}")

def handle_backend_response(arduino, response):
    """Process backend JSON response and send appropriate command to Arduino"""
    print(f"🔍 Processing backend response...")
    print(f"📄 Full response: {response}")
    
    # Extract decision from your backend format
    decision = response.get('decision', '').lower()
    keyword_present = response.get('keyword_present', False)
    best_match = response.get('best_match', {})
    
    # Get speaker information
    speaker_name = best_match.get('name', 'Unknown')
    similarity = best_match.get('similarity', 0.0)
    member_id = best_match.get('member_id', 'N/A')
    
    # Get keyword information
    keyword_hits = response.get('keyword_hits', [])
    detected_keywords = [kw.get('keyword', '') for kw in keyword_hits]
    
    # Get configuration thresholds
    config = response.get('config', {})
    speaker_threshold = config.get('speaker_threshold', 0.8)
    
    print(f"👤 Speaker: {speaker_name}")
    print(f"📊 Similarity: {similarity:.4f} (threshold: {speaker_threshold})")
    print(f"🔑 Keywords detected: {', '.join(detected_keywords) if detected_keywords else 'None'}")
    print(f"✅ Keyword present: {keyword_present}")
    print(f"⚖️ Decision: {decision}")
    
    # Decision logic based on your backend response
    if decision == "accepted" and keyword_present:
        print("✅ ACCESS GRANTED - Opening door")
        print(f"   Authorized user: {speaker_name}")
        print(f"   Similarity score: {similarity:.2%}")
        send_command_to_arduino(arduino, "OPEN_DOOR")
        # Door will auto-close after 5 seconds on Arduino
    else:
        print("❌ ACCESS DENIED")
        
        # Detailed rejection reason
        if not keyword_present:
            print("   Reason: Required keyword not detected")
        elif decision == "rejected":
            if similarity < speaker_threshold:
                print(f"   Reason: Speaker similarity ({similarity:.2%}) below threshold ({speaker_threshold:.0%})")
            else:
                print("   Reason: Authentication requirements not met")
        
        send_command_to_arduino(arduino, "ACCESS_DENIED")

if __name__ == "__main__":
    main()