#include <Arduino.h>
#include <WiFi.h>
#include <WebServer.h>
#include <ArduinoJson.h>

#ifndef WIFI_SSID
#error "WIFI_SSID is not defined. Set it via build_flags in platformio.ini."
#endif
#ifndef WIFI_PASSWORD
#error "WIFI_PASSWORD is not defined. Set it via build_flags in platformio.ini."
#endif

WebServer server(80);

void handleGetTools()
{
    JsonDocument doc;

    JsonArray tools = doc["tools"].to<JsonArray>();

    JsonObject t1 = tools.add<JsonObject>();
    t1["name"] = "gpio_write";
    t1["description"] = "Set a digital pin HIGH or LOW. Args: pin (int), value (0 or 1)";

    JsonObject t2 = tools.add<JsonObject>();
    t2["name"] = "gpio_read";
    t2["description"] = "Read a digital pin. Args: pin (int)";

    JsonObject t3 = tools.add<JsonObject>();
    t3["name"] = "adc_read";
    t3["description"] = "Read analog value 0-4095. Args: pin (int)";

    JsonObject t4 = tools.add<JsonObject>();
    t4["name"] = "pwm_write";
    t4["description"] = "Write PWM 0-255. Args: pin (int), duty (int)";

    String out;
    serializeJson(doc, out);
    server.send(200, "application/json", out);
}

void handleCall()
{
    if (!server.hasArg("plain"))
    {
        server.send(400, "application/json", "{\"error\": \"No body\"}");
        return;
    }

    String body = server.arg("plain");
    JsonDocument req;
    DeserializationError err = deserializeJson(req, body);

    if (err)
    {
        server.send(400, "application/json", "{\"error\": \"Invalid JSON\"}");
        return;
    }

    const char *tool = req["tool"];
    int pin = req["args"]["pin"] | -1;

    if (pin < 0)
    {
        server.send(400, "application/json", "{\"error\": \"Missing pin argument\"}");
        return;
    }

    JsonDocument res;

    if (strcmp(tool, "gpio_write") == 0)
    {
        int value = req["args"]["value"] | 0;
        pinMode(pin, OUTPUT);
        digitalWrite(pin, value ? HIGH : LOW);
        res["success"] = true;
        res["pin"] = pin;
        res["value"] = value;
    }
    else if (strcmp(tool, "gpio_read") == 0)
    {
        pinMode(pin, INPUT);
        int value = digitalRead(pin);
        res["success"] = true;
        res["pin"] = pin;
        res["value"] = value;
    }
    else if (strcmp(tool, "adc_read") == 0)
    {
        int raw = analogRead(pin);
        res["success"] = true;
        res["pin"] = pin;
        res["raw"] = raw;
        res["voltage"] = (raw * 3.3) / 4095.0;
    }
    else if (strcmp(tool, "pwm_write") == 0)
    {
        int duty = req["args"]["duty"] | 0;
        pinMode(pin, OUTPUT);
        analogWrite(pin, duty);
        res["success"] = true;
        res["pin"] = pin;
        res["duty"] = duty;
    }
    else
    {
        res["success"] = false;
        res["error"] = "Unknown tool";
        String out;
        serializeJson(res, out);
        server.send(404, "application/json", out);
        return;
    }

    String out;
    serializeJson(res, out);
    server.send(200, "application/json", out);
}

void setup()
{
    Serial.begin(115200);

    WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
    Serial.print("Connecting to WiFi");
    while (WiFi.status() != WL_CONNECTED)
    {
        delay(500);
        Serial.print(".");
    }
    Serial.println();
    Serial.print("IP: ");
    Serial.println(WiFi.localIP());

    server.on("/tools", HTTP_GET, handleGetTools);
    server.on("/call", HTTP_POST, handleCall);
    server.begin();
    Serial.println("Tool server ready");
}

void loop()
{
    server.handleClient();
}
