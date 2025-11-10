#include <Servo.h>

// Pin definitions
int greenLED = 7;  // Success LED
int redLED = 6;    // Error / denied LED
int buzzer = 8;    // Buzzer
int servoPin = 9;  // Servo pin
int buttonPin = 2; // Push button pin

Servo doorServo;
int wrongAttempts = 0; // Count invalid commands
String command = "";

// Button debouncing
bool lastButtonState = HIGH;
bool currentButtonState = HIGH;
unsigned long lastDebounceTime = 0;
const unsigned long debounceDelay = 50;

// Door auto-close timer
unsigned long doorOpenTime = 0;
const unsigned long DOOR_OPEN_DURATION = 5000; // 5 seconds
bool isDoorOpen = false;

void setup()
{
  pinMode(greenLED, OUTPUT);
  pinMode(redLED, OUTPUT);
  pinMode(buzzer, OUTPUT);
  pinMode(buttonPin, INPUT_PULLUP); // Button with internal pull-up
  doorServo.attach(servoPin);

  Serial.begin(9600);
  Serial.println("Arduino ready for door commands!");

  closeDoor(); // Start with door closed
}

void loop()
{
  // 1️⃣ Check button press with debouncing
  int reading = digitalRead(buttonPin);

  if (reading != lastButtonState)
  {
    lastDebounceTime = millis();
  }

  if ((millis() - lastDebounceTime) > debounceDelay)
  {
    if (reading != currentButtonState)
    {
      currentButtonState = reading;

      // Button pressed (LOW because of INPUT_PULLUP)
      if (currentButtonState == LOW)
      {
        Serial.println("BUTTON_PRESSED"); // Notify Pi to record audio
      }
    }
  }

  lastButtonState = reading;

  // 2️⃣ Check Pi commands via serial
  if (Serial.available())
  {
    command = Serial.readStringUntil('\n');
    command.trim();
    Serial.print("Received command: ");
    Serial.println(command);

    if (command == "OPEN_DOOR")
    {
      openDoor();
    }
    else if (command == "CLOSE_DOOR")
    {
      closeDoor();
    }
    else if (command == "ACCESS_DENIED")
    {
      accessDenied();
    }
    else if (command == "OPEN") // Backward compatibility
    {
      openDoor();
    }
    else if (command == "CLOSE") // Backward compatibility
    {
      closeDoor();
    }
    else
    {
      invalidCommand();
    }
  }

  // 3️⃣ Auto-close door after duration
  if (isDoorOpen && (millis() - doorOpenTime >= DOOR_OPEN_DURATION))
  {
    closeDoor();
  }

  delay(10);
}

void openDoor()
{
  wrongAttempts = 0;
  isDoorOpen = true;
  doorOpenTime = millis();

  Serial.println("DOOR_OPENED");
  Serial.println("✅ Door Opened");

  digitalWrite(greenLED, HIGH);
  digitalWrite(redLED, LOW);

  // Smooth servo movement to open
  for (int pos = 0; pos <= 90; pos += 5)
  {
    doorServo.write(pos);
    delay(20);
  }

  // Success beep pattern
  for (int i = 0; i < 3; i++)
  {
    tone(buzzer, 1000);
    delay(200);
    noTone(buzzer);
    delay(200);
  }

  digitalWrite(greenLED, LOW);
}

void closeDoor()
{
  isDoorOpen = false;
  Serial.println("DOOR_CLOSED");
  Serial.println("🚪 Door Closed");

  digitalWrite(greenLED, LOW);
  digitalWrite(redLED, LOW);

  // Smooth servo movement to close
  for (int pos = 90; pos >= 0; pos -= 5)
  {
    doorServo.write(pos);
    delay(20);
  }

  // Closing sound
  tone(buzzer, 600);
  delay(300);
  noTone(buzzer);
  delay(150);
  tone(buzzer, 400);
  delay(300);
  noTone(buzzer);
}

void accessDenied()
{
  wrongAttempts++;
  Serial.println("ACCESS_DENIED_ACK");
  Serial.println("❌ Access Denied");

  // Flash red LED and beep
  for (int i = 0; i < 3; i++)
  {
    digitalWrite(redLED, HIGH);
    tone(buzzer, 300);
    delay(200);
    digitalWrite(redLED, LOW);
    noTone(buzzer);
    delay(200);
  }

  // Check for multiple failed attempts
  if (wrongAttempts >= 3)
  {
    alertMode();
  }
}

void invalidCommand()
{
  wrongAttempts++;
  Serial.println("❌ Invalid Command");
  digitalWrite(redLED, HIGH);
  tone(buzzer, 200);
  delay(500);
  noTone(buzzer);
  digitalWrite(redLED, LOW);

  if (wrongAttempts >= 3)
  {
    alertMode();
  }
}

void alertMode()
{
  Serial.println("🚨 ALERT! Multiple wrong attempts!");

  // Alert pattern - 10 cycles
  for (int i = 0; i < 10; i++)
  {
    digitalWrite(redLED, HIGH);
    tone(buzzer, 700);
    delay(200);
    digitalWrite(redLED, LOW);
    noTone(buzzer);
    delay(200);
  }

  wrongAttempts = 0; // Reset counter
}