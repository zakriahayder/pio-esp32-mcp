#include <Arduino.h>

const int LED_PIN = 2; // onboard LED on ESP32

void setup()
{
    Serial.begin(115200);
    pinMode(LED_PIN, OUTPUT);
    Serial.println("Blink example ready");
}

void loop()
{
    digitalWrite(LED_PIN, HIGH);
    Serial.println("LED ON");
    delay(1000);
    digitalWrite(LED_PIN, LOW);
    Serial.println("LED OFF");
    delay(1000);
}
