#include <OneWire.h>
#include <DallasTemperature.h>
#include <Wire.h>
#include <LiquidCrystal_I2C.h>
#include <DHT.h>

#define ONE_WIRE_BUS 3
#define BUZZER_PIN 7
#define LED_PIN_COLD 8
#define LED_PIN_WARM 9
#define LED_PIN_HOT 10
#define MAX_TEMPERATURE 40
#define COLD_THRESHOLD 18
#define WARM_THRESHOLD 40
#define DHT_PIN 4
#define MQ135_PIN A1                                                                                                              
#define BUTTON_PIN 11  // Pin for the push button switch

// Add these constants for air quality thresholds
#define GOOD_AIR_QUALITY_THRESHOLD 200 // Define your threshold values here
#define MODERATE_AIR_QUALITY_THRESHOLD 400 // Define your threshold values here

OneWire oneWire(ONE_WIRE_BUS);
DallasTemperature sensors(&oneWire);
LiquidCrystal_I2C lcd(0x27, 16, 2);
DHT dht(DHT_PIN, DHT22);

int currentSensor = 0;
bool buttonPressed = false;

void setup() {
  lcd.init();
  lcd.backlight();

  sensors.begin();
  dht.begin();
  Serial.begin(9600);

  pinMode(BUZZER_PIN, OUTPUT);
  pinMode(LED_PIN_COLD, OUTPUT);
  pinMode(LED_PIN_WARM, OUTPUT);
  pinMode(LED_PIN_HOT, OUTPUT);
  pinMode(BUTTON_PIN, INPUT_PULLUP);  // Set the button pin as input with internal pull-up resistor
}

void loop() {
  sensors.requestTemperatures();
  float temperatureDS18B20 = sensors.getTempCByIndex(0);
  float humidity = dht.readHumidity();
  float temperatureDHT22 = dht.readTemperature();
  int mq135Value = analogRead(MQ135_PIN);
  int buttonState = digitalRead(BUTTON_PIN);

  // Check if the button was pressed
  if (buttonState == LOW && !buttonPressed) {
    currentSensor = (currentSensor + 1) % 3; // Change the display
    buttonPressed = true;
  } else if (buttonState == HIGH) {
    buttonPressed = false;
  }

  // Update LCD display with sensor data
  lcd.clear();
  displaySensor(currentSensor, temperatureDS18B20, temperatureDHT22, mq135Value);

  // Print sensor data to serial monitor
  Serial.print("Temperature DS18B20: ");
  Serial.print(temperatureDS18B20);
  Serial.println(" C");
  Serial.print("Temperature DHT22: ");
  Serial.print(temperatureDHT22);
  Serial.println(" C");
  Serial.print("MQ135 Value: ");
  Serial.println(mq135Value);

  if (temperatureDS18B20 > MAX_TEMPERATURE || temperatureDHT22 > MAX_TEMPERATURE) {
    buzzerAlert(); // Activate the buzzer alert
  }

  // Update LED indicators based on sensor data
  if (temperatureDS18B20 < COLD_THRESHOLD) {
    digitalWrite(LED_PIN_COLD, HIGH);
    digitalWrite(LED_PIN_WARM, LOW);
    digitalWrite(LED_PIN_HOT, LOW);
  } else if (temperatureDS18B20 >= COLD_THRESHOLD && temperatureDS18B20 < WARM_THRESHOLD) {
    digitalWrite(LED_PIN_COLD, LOW);
    digitalWrite(LED_PIN_WARM, HIGH);
    digitalWrite(LED_PIN_HOT, LOW);
  } else {
    digitalWrite(LED_PIN_COLD, LOW);
    digitalWrite(LED_PIN_WARM, LOW);
    digitalWrite(LED_PIN_HOT, HIGH);
  }
}


void buzzerAlert() {
  for (int i = 0; i < 3; i++) {
    tone(BUZZER_PIN, 5000); // Activate the buzzer with a frequency of 5000 Hz
    delay(200); // Buzzer on for 200 milliseconds
    noTone(BUZZER_PIN); // Turn off the buzzer
    delay(200); // Delay between each "bip"
  }
}

void displaySensor(int sensorIndex, float temperatureDS18B20, float temperatureDHT22, int mq135Value) {
  lcd.setCursor(0, 0);
  if (sensorIndex == 0) {
    lcd.print("DS18B20 Temp:");
    lcd.setCursor(0, 1);
    lcd.print(temperatureDS18B20);
    lcd.write(223); // Degree symbol (°)
    lcd.print("C");
  } else if (sensorIndex == 1) {
    lcd.print("DHT22 Temp:");
    lcd.setCursor(0, 1);
    lcd.print(temperatureDHT22);
    lcd.write(223); // Degree symbol (°)
    lcd.print("C");
  } else if (sensorIndex == 2) {
    lcd.print("MQ135 PPM:");
    lcd.setCursor(0, 1);
    lcd.print(mq135Value);
        // Interpret MQ135 sensor data and display air quality indicator
    if (mq135Value < GOOD_AIR_QUALITY_THRESHOLD) {
      // Good air quality
      lcd.setCursor(5, 1);
      lcd.print("(Good)");
    } else if (mq135Value < MODERATE_AIR_QUALITY_THRESHOLD) {
      // Moderate air quality
      lcd.setCursor(5, 1);
      lcd.print("(Moderate)");
    } else {
      // Poor air quality
      lcd.setCursor(5, 1);
      lcd.print("(Poor)");
    }
  }
}
