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
  // 1️⃣ Check button press
  if (digitalRead(buttonPin) == LOW) // pressed (LOW because of pull-up)
  {
    Serial.println("BUTTON_PRESSED"); // Notify Pi to record audio
    delay(300);                       // Debounce & prevent multiple signals
  }

  // 2️⃣ Check Pi commands via serial
  if (Serial.available())
  {
    command = Serial.readStringUntil('\n');
    command.trim();
    Serial.print("Received command: ");
    Serial.println(command);

    if (command == "OPEN")
    {
      openDoor();
    }
    else if (command == "CLOSE")
    {
      closeDoor();
    }
    else
    {
      invalidCommand();
    }
  }
}

void openDoor()
{
  wrongAttempts = 0;
  Serial.println("✅ Door Opened");
  digitalWrite(greenLED, HIGH);
  digitalWrite(redLED, LOW);

  for (int pos = 0; pos <= 90; pos += 5)
  {
    doorServo.write(pos);
    delay(20);
  }

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
  wrongAttempts = 0;
  Serial.println("🚪 Door Closed");
  digitalWrite(greenLED, LOW);
  digitalWrite(redLED, LOW);

  for (int pos = 90; pos >= 0; pos -= 5)
  {
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
  for (int i = 0; i < 10; i++)
  {
    digitalWrite(redLED, HIGH);
    tone(buzzer, 700);
    delay(200);
    digitalWrite(redLED, LOW);
    delay(200);
  }
  noTone(buzzer);
  wrongAttempts = 0; // reset counter
}
