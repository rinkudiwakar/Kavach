#include <Servo.h>
#include <Keypad.h>

// Pin definitions
int greenLED = 7;   // Success LED
int redLED = 6;     // Error LED
int buzzer = 8;     // Buzzer
int servoPin = 9;   // Servo pin
int buttonPin = 2;  // Push button pin

Servo doorServo;

// Keypad setup
const byte ROWS = 4;
const byte COLS = 3;
char keys[ROWS][COLS] = {
  {'1', '2', '3'},
  {'4', '5', '6'},
  {'7', '8', '9'},
  {'*', '0', '#'}
};
byte rowPins[ROWS] = {A0, A1, A2, A3};
byte colPins[COLS] = {A4, A5, 10};

// Create keypad object
Keypad keypad = Keypad(makeKeymap(keys), rowPins, colPins, ROWS, COLS);

// Default password
String defaultPassword = "1234";
String enteredPassword = "";

// Variables
int wrongAttempts = 0;
String command = "";

// Button state tracking
bool lastButtonState = HIGH; // Using INPUT_PULLUP
bool currentButtonState = HIGH;

// Door auto-close timer
unsigned long doorOpenTime = 0;
const unsigned long DOOR_OPEN_DURATION = 5000;
bool isDoorOpen = false;

void setup() {
  pinMode(greenLED, OUTPUT);
  pinMode(redLED, OUTPUT);
  pinMode(buzzer, OUTPUT);
  pinMode(buttonPin, INPUT_PULLUP);
  doorServo.attach(servoPin);

  Serial.begin(9600);
  Serial.println("Arduino ready for door commands!");

  closeDoor();
}

void loop() {
  // 🎙️ Button Hold-to-Record Mode
  currentButtonState = digitalRead(buttonPin);

  if (currentButtonState != lastButtonState) {
    // Button pressed (LOW)
    if (currentButtonState == LOW) {
      Serial.println("RECORD_START");
      digitalWrite(redLED, HIGH);
      tone(buzzer, 800);
      delay(100);
      noTone(buzzer);
    }
    // Button released (HIGH)
    else if (currentButtonState == HIGH) {
      Serial.println("RECORD_STOP");
      digitalWrite(redLED, LOW);
      tone(buzzer, 400);
      delay(100);
      noTone(buzzer);
    }
    lastButtonState = currentButtonState;
  }

  // 🧠 Check Raspberry Pi serial commands
  if (Serial.available()) {
    command = Serial.readStringUntil('\n');
    command.trim();
    Serial.print("Received command: ");
    Serial.println(command);

    if (command == "OPEN_DOOR" || command == "OPEN") {
      openDoor();
    } else if (command == "CLOSE_DOOR" || command == "CLOSE") {
      closeDoor();
    } else if (command == "ACCESS_DENIED") {
      accessDenied();
    } else {
      invalidCommand();
    }
  }

  // ⌨️ Keypad input for manual access
  char key = keypad.getKey();
  if (key) {
    if (key == '#') { // Submit
      if (enteredPassword == defaultPassword) {
        Serial.println("KEYPAD_ACCESS_GRANTED");
        openDoor();
      } else {
        Serial.println("KEYPAD_ACCESS_DENIED");
        accessDenied();
      }
      enteredPassword = "";
    } else if (key == '*') { // Clear
      enteredPassword = "";
      Serial.println("Password cleared");
    } else {
      enteredPassword += key;
      Serial.print("*");
    }
  }

  // ⏱ Auto-close door
  if (isDoorOpen && (millis() - doorOpenTime >= DOOR_OPEN_DURATION)) {
    closeDoor();
  }

  delay(10);
}

void openDoor() {
  wrongAttempts = 0;
  isDoorOpen = true;
  doorOpenTime = millis();

  Serial.println("DOOR_OPENED");
  digitalWrite(greenLED, HIGH);
  digitalWrite(redLED, LOW);

  for (int pos = 0; pos <= 90; pos += 5) {
    doorServo.write(pos);
    delay(20);
  }

  // Success beep
  for (int i = 0; i < 3; i++) {
    tone(buzzer, 1000);
    delay(200);
    noTone(buzzer);
    delay(200);
  }

  digitalWrite(greenLED, LOW);
}

void closeDoor() {
  isDoorOpen = false;
  Serial.println("DOOR_CLOSED");

  digitalWrite(greenLED, LOW);
  digitalWrite(redLED, LOW);

  for (int pos = 90; pos >= 0; pos -= 5) {
    doorServo.write(pos);
    delay(20);
  }

  tone(buzzer, 600);
  delay(300);
  noTone(buzzer);
  delay(150);
  tone(buzzer, 400);
  delay(300);
  noTone(buzzer);
}

void accessDenied() {
  wrongAttempts++;
  Serial.println("ACCESS_DENIED_ACK");

  for (int i = 0; i < 3; i++) {
    digitalWrite(redLED, HIGH);
    tone(buzzer, 300);
    delay(200);
    digitalWrite(redLED, LOW);
    noTone(buzzer);
    delay(200);
  }

  if (wrongAttempts >= 3) {
    alertMode();
  }
}

void invalidCommand() {
  wrongAttempts++;
  Serial.println("❌ Invalid Command");
  digitalWrite(redLED, HIGH);
  tone(buzzer, 200);
  delay(500);
  noTone(buzzer);
  digitalWrite(redLED, LOW);

  if (wrongAttempts >= 3) {
    alertMode();
  }
}

void alertMode() {
  Serial.println("🚨 ALERT! Multiple wrong attempts!");

  for (int i = 0; i < 10; i++) {
    digitalWrite(redLED, HIGH);
    tone(buzzer, 700);
    delay(200);
    digitalWrite(redLED, LOW);
    noTone(buzzer);
    delay(200);
  }

  wrongAttempts = 0;
}
