#include <Wire.h>

const int buttonPin = 2;
const int MPU6050_ADDR = 0x68;

// Ultrasonic sensor pins
const int trigPin = 9;
const int echoPin = 10;

int16_t ax, ay, az;
bool buttonPressed = false;

// Double press variables
unsigned long lastPressTime = 0;
int pressCount = 0;
const unsigned long doublePressInterval = 500;
bool dataSendingEnabled = true;

void setup() {
  Serial.begin(9600);
  Wire.begin();
  pinMode(buttonPin, INPUT_PULLUP);

  pinMode(trigPin, OUTPUT);
  pinMode(echoPin, INPUT);

  Wire.beginTransmission(MPU6050_ADDR);
  Wire.write(0x6B);
  Wire.write(0);
  Wire.endTransmission(true);
  delay(100);
}

long measureDistance() {
  digitalWrite(trigPin, LOW);
  delayMicroseconds(2);
  digitalWrite(trigPin, HIGH);
  delayMicroseconds(10);
  digitalWrite(trigPin, LOW);

  long duration = pulseIn(echoPin, HIGH);
  return duration * 0.034 / 2;
}

void loop() {
  bool currentButtonState = (digitalRead(buttonPin) == LOW);

  // Detect button press (falling edge)
  if (currentButtonState != buttonPressed) {
    buttonPressed = currentButtonState;
    
    if (buttonPressed) {
      unsigned long now = millis();
      
      if (now - lastPressTime <= doublePressInterval) {
        pressCount++;
      } else {
        pressCount = 1;
      }
      lastPressTime = now;

      if (pressCount == 2) {
        dataSendingEnabled = !dataSendingEnabled;
        pressCount = 0;
        Serial.print("Mode: ");
        Serial.println(dataSendingEnabled ? "Data Enabled" : "Button Only");
      }
    }
  }

  if (dataSendingEnabled) {
    // Read accelerometer
    Wire.beginTransmission(MPU6050_ADDR);
    Wire.write(0x3B);
    Wire.endTransmission(false);
    Wire.requestFrom(MPU6050_ADDR, 6, true);
    ax = (Wire.read() << 8) | Wire.read();
    ay = (Wire.read() << 8) | Wire.read();
    az = (Wire.read() << 8) | Wire.read();

    float roll = atan2(ay / 16384.0, az / 16384.0) * 180 / PI;

    // Read temperature
    Wire.beginTransmission(MPU6050_ADDR);
    Wire.write(0x41);
    Wire.endTransmission(false);
    Wire.requestFrom(MPU6050_ADDR, 2, true);
    int16_t tempRaw = (Wire.read() << 8) | Wire.read();
    float temperature = (tempRaw / 340.0) + 36.53;

    // Determine posture
    String posture = (roll > -100 || roll < -200) ? "Bad" : "Good";

    // Measure distance
    long distance = measureDistance();

    // Output all data
    Serial.print("Roll: ");
    Serial.print(roll);
    Serial.print("°, Temp: ");
    Serial.print(temperature);
    Serial.print("°C, ");
    Serial.print(", Posture: ");
    Serial.print(posture);
    Serial.print(", Distance: ");
    Serial.print(distance);
    Serial.print("cm, Button: ");
    Serial.println(buttonPressed ? "Yes" : "No");
  } else {
    // Output only button status
    Serial.print("Button Pressed: ");
    Serial.println(buttonPressed ? "Yes" : "No");
  }

  delay(3000);
}
