#include <Arduino.h>
#include <ArduinoJson.h>
#include <DHT.h>
#include <TinyGPS++.h>
#include <WiFi.h>
#include <PubSubClient.h>
#include <string.h>
#include <time.h>

// ESP32 DevKit boards commonly route the onboard LED to GPIO2.
#ifndef LED_BUILTIN
#define LED_BUILTIN 2
#endif

constexpr uint32_t kSerialBaudRate = 115200;
constexpr uint32_t kBlinkIntervalMs = 500;
constexpr uint32_t kDhtPollIntervalMs = 1000;
constexpr uint32_t kGpsStatusIntervalMs = 1000;
constexpr uint32_t kFuseStatusIntervalMs = 5000;
constexpr uint32_t kTelemetryIntervalMs = 2000;
constexpr uint32_t kWifiReconnectIntervalMs = 10000;
constexpr uint32_t kMqttReconnectIntervalMs = 5000;
constexpr size_t kZoneCount = 3;
constexpr size_t kTelemetryQueueSize = 5;
constexpr size_t kTelemetryPayloadSize = 1024;

constexpr uint8_t kDhtZone1Pin = 4;
constexpr uint8_t kDhtZone2Pin = 23;
constexpr uint8_t kDhtZone3Pin = 27;
constexpr uint8_t kFuseStableReadCount = 3;
constexpr uint8_t kGpsRxPin = 16;
constexpr uint8_t kGpsTxPin = 17;
constexpr uint32_t kGpsBaudRate = 9600;
constexpr uint8_t kFanPin = 18;
constexpr uint8_t kBuzzerPin = 19;
constexpr uint8_t kStatusLed1Pin = 21;
constexpr uint8_t kStatusLed2Pin = 22;

constexpr char kWifiSsid[] = "Ritvik";
constexpr char kWifiPassword[] = "12345678";
constexpr char kMqttHost[] = "10.110.196.48";
constexpr uint16_t kMqttPort = 1883;
constexpr char kMqttClientId[] = "predictfuse-esp32";
constexpr char kTelemetryTopic[] = "coldguard/telemetry";
constexpr char kActuateTopic[] = "coldguard/actuate";

DHT dhtZone1(kDhtZone1Pin, DHT11);
DHT dhtZone2(kDhtZone2Pin, DHT11);
DHT dhtZone3(kDhtZone3Pin, DHT11);
TinyGPSPlus gps;
WiFiClient wifiClient;
PubSubClient mqttClient(wifiClient);

struct ZoneReading {
  float temperatureC;
  float humidityPct;
  bool valid;
};

ZoneReading zoneReadings[kZoneCount] = {};

struct FuseInput {
  uint8_t zoneId;
  uint8_t pin;
  bool stableOpen;
  bool candidateOpen;
  uint8_t candidateReads;
  bool fuseTriggered;
  float triggerTemperatureC;
};

FuseInput fuseInputs[] = {
    {1, 32, false, false, 0, false, NAN},
    {2, 33, false, false, 0, false, NAN},
    {3, 25, false, false, 0, false, NAN},
};

struct TelemetryQueue {
  char messages[kTelemetryQueueSize][kTelemetryPayloadSize];
  size_t head;
  size_t count;
};

TelemetryQueue telemetryQueue = {};

uint32_t lastBlinkMs = 0;
uint32_t lastDhtPollMs = 0;
uint32_t lastGpsStatusMs = 0;
uint32_t lastFuseStatusMs = 0;
uint32_t lastTelemetryMs = 0;
uint32_t lastWifiAttemptMs = 0;
uint32_t lastMqttAttemptMs = 0;
bool timeConfigured = false;

void setFan(bool on) {
  digitalWrite(kFanPin, on ? HIGH : LOW);
  digitalWrite(kStatusLed1Pin, on ? HIGH : LOW);
}

void setBuzzer(bool on) {
  digitalWrite(kBuzzerPin, on ? HIGH : LOW);
  digitalWrite(kStatusLed2Pin, on ? HIGH : LOW);
}

void handleActuation(char *topic, byte *payload, unsigned int length) {
  if (strcmp(topic, kActuateTopic) != 0) {
    return;
  }

  StaticJsonDocument<512> document;
  if (deserializeJson(document, payload, length)) {
    Serial.println("Actuation: invalid JSON");
    return;
  }

  const char *peltierState = document["peltier_state"];
  if (peltierState != nullptr) {
    if (strcmp(peltierState, "ON") == 0) {
      setFan(true);
    } else if (strcmp(peltierState, "OFF") == 0) {
      setFan(false);
    }
  }

  const char *buzzerState = document["alert_buzzer"];
  if (buzzerState != nullptr) {
    if (strcmp(buzzerState, "ON") == 0) {
      setBuzzer(true);
    } else if (strcmp(buzzerState, "OFF") == 0) {
      setBuzzer(false);
    }
  }

  const int targetZoneId = document["target_zone_id"] | 0;
  const char *servoVentPosition = document["servo_vent_position"] | "";
  Serial.printf("Actuation: target_zone_id=%d servo_vent_position=%s\n",
                targetZoneId, servoVentPosition);
}

void readAndPrintZone(uint8_t zoneId, DHT &sensor, ZoneReading &reading) {
  const float humidityPct = sensor.readHumidity();
  const float temperatureC = sensor.readTemperature();

  if (isnan(humidityPct) || isnan(temperatureC)) {
    reading.valid = false;
    Serial.printf("Zone %u: DHT11 read failed\n", zoneId);
    return;
  }

  reading.temperatureC = temperatureC;
  reading.humidityPct = humidityPct;
  reading.valid = true;
  Serial.printf("Zone %u: %.0f C, %.0f %% RH\n", zoneId, temperatureC,
                humidityPct);
}

void initializeFuseInput(FuseInput &fuse) {
  pinMode(fuse.pin, INPUT_PULLUP);
  fuse.stableOpen = digitalRead(fuse.pin) == HIGH;
  fuse.candidateOpen = fuse.stableOpen;
  fuse.candidateReads = 0;
  fuse.fuseTriggered = fuse.stableOpen;
  fuse.triggerTemperatureC = NAN;
}

void pollFuseInput(FuseInput &fuse, const ZoneReading &reading,
                   uint32_t timestampMs) {
  const bool isOpen = digitalRead(fuse.pin) == HIGH;

  if (isOpen == fuse.stableOpen) {
    fuse.candidateOpen = isOpen;
    fuse.candidateReads = 0;
    return;
  }

  if (isOpen != fuse.candidateOpen) {
    fuse.candidateOpen = isOpen;
    fuse.candidateReads = 1;
    return;
  }

  if (++fuse.candidateReads < kFuseStableReadCount) {
    return;
  }

  fuse.stableOpen = fuse.candidateOpen;
  fuse.candidateReads = 0;
  if (fuse.stableOpen && !fuse.fuseTriggered) {
    fuse.fuseTriggered = true;
    fuse.triggerTemperatureC =
        reading.valid ? reading.temperatureC : NAN;
  }
  Serial.printf("timestamp_ms=%lu zone_id=%u fuse_state=%s\n", timestampMs,
                fuse.zoneId, fuse.stableOpen ? "OPEN" : "CLOSED");
}

void printFuseStatus(uint32_t timestampMs) {
  for (const FuseInput &fuse : fuseInputs) {
    Serial.printf(
        "Fuse status: timestamp_ms=%lu zone_id=%u fuse_state=%s "
        "fuse_triggered=%s\n",
        timestampMs, fuse.zoneId, fuse.stableOpen ? "OPEN" : "CLOSED",
        fuse.fuseTriggered ? "true" : "false");
  }
}

void parseGpsData() {
  while (Serial2.available() > 0) {
    gps.encode(Serial2.read());
  }
}

void printGpsStatus() {
  if (!gps.location.isValid()) {
    Serial.println("GPS: NO FIX");
    return;
  }

  Serial.printf("GPS: FIX lat=%.6f lng=%.6f\n", gps.location.lat(),
                gps.location.lng());
}

bool formatUtcTimestamp(char *timestamp, size_t timestampSize) {
  if (gps.date.isValid() && gps.time.isValid()) {
    snprintf(timestamp, timestampSize, "%04d-%02d-%02dT%02d:%02d:%02dZ",
             gps.date.year(), gps.date.month(), gps.date.day(),
             gps.time.hour(), gps.time.minute(), gps.time.second());
    return true;
  }

  const time_t now = time(nullptr);
  if (now < 1704067200) {
    return false;
  }

  tm utcTime;
  gmtime_r(&now, &utcTime);
  return strftime(timestamp, timestampSize, "%Y-%m-%dT%H:%M:%SZ", &utcTime) >
         0;
}

bool buildTelemetry(char *payload, size_t payloadSize) {
  char timestamp[21];
  if (!formatUtcTimestamp(timestamp, sizeof(timestamp))) {
    return false;
  }

  float ambientTemperatureC = 0.0f;
  float ambientHumidityPct = 0.0f;
  for (size_t index = 0; index < kZoneCount; ++index) {
    if (!zoneReadings[index].valid) {
      return false;
    }
    ambientTemperatureC += zoneReadings[index].temperatureC;
    ambientHumidityPct += zoneReadings[index].humidityPct;
  }
  ambientTemperatureC /= kZoneCount;
  ambientHumidityPct /= kZoneCount;

  StaticJsonDocument<1024> document;
  document["timestamp"] = timestamp;
  JsonObject ambient = document.createNestedObject("ambient");
  ambient["temp_c"] = ambientTemperatureC;
  ambient["humidity_pct"] = ambientHumidityPct;

  JsonObject gpsData = document.createNestedObject("gps");
  if (gps.location.isValid()) {
    gpsData["lat"] = gps.location.lat();
    gpsData["lng"] = gps.location.lng();
  } else {
    gpsData["lat"] = nullptr;
    gpsData["lng"] = nullptr;
  }

  JsonArray zones = document.createNestedArray("zones");
  for (size_t index = 0; index < kZoneCount; ++index) {
    const FuseInput &fuse = fuseInputs[index];
    JsonObject zone = zones.createNestedObject();
    zone["zone_id"] = fuse.zoneId;
    zone["temp_c"] = zoneReadings[index].temperatureC;
    zone["fuse_triggered"] = fuse.fuseTriggered;
    zone["vial_id"] = nullptr;
    zone["fuse_level"] = nullptr;
    if (fuse.fuseTriggered && !isnan(fuse.triggerTemperatureC)) {
      zone["trigger_temp_c"] = fuse.triggerTemperatureC;
    } else {
      zone["trigger_temp_c"] = nullptr;
    }
  }

  const size_t serialized = serializeJson(document, payload, payloadSize);
  return serialized > 0 && serialized < payloadSize;
}

void queueTelemetry(const char *payload) {
  if (telemetryQueue.count == kTelemetryQueueSize) {
    telemetryQueue.head = (telemetryQueue.head + 1) % kTelemetryQueueSize;
    --telemetryQueue.count;
  }

  const size_t tail =
      (telemetryQueue.head + telemetryQueue.count) % kTelemetryQueueSize;
  snprintf(telemetryQueue.messages[tail], kTelemetryPayloadSize, "%s", payload);
  ++telemetryQueue.count;
}

void flushTelemetryQueue() {
  while (mqttClient.connected() && telemetryQueue.count > 0) {
    const char *payload = telemetryQueue.messages[telemetryQueue.head];
    if (!mqttClient.publish(kTelemetryTopic, payload)) {
      return;
    }
    telemetryQueue.head = (telemetryQueue.head + 1) % kTelemetryQueueSize;
    --telemetryQueue.count;
  }
}

void maintainNetwork(uint32_t now) {
  if (WiFi.status() != WL_CONNECTED) {
    if (mqttClient.connected()) {
      mqttClient.disconnect();
    }
    if (now - lastWifiAttemptMs >= kWifiReconnectIntervalMs) {
      lastWifiAttemptMs = now;
      WiFi.begin(kWifiSsid, kWifiPassword);
    }
    return;
  }

  if (!timeConfigured) {
    configTime(0, 0, "pool.ntp.org", "time.nist.gov");
    timeConfigured = true;
  }

  if (!mqttClient.connected()) {
    if (now - lastMqttAttemptMs >= kMqttReconnectIntervalMs) {
      lastMqttAttemptMs = now;
      if (mqttClient.connect(kMqttClientId)) {
        mqttClient.subscribe(kActuateTopic);
      }
    }
    return;
  }

  mqttClient.loop();
  flushTelemetryQueue();
}

void setup() {
  Serial.begin(kSerialBaudRate);
  pinMode(LED_BUILTIN, OUTPUT);
  digitalWrite(LED_BUILTIN, LOW);
  dhtZone1.begin();
  dhtZone2.begin();
  dhtZone3.begin();
  Serial2.begin(kGpsBaudRate, SERIAL_8N1, kGpsRxPin, kGpsTxPin);
  WiFi.mode(WIFI_STA);
  WiFi.begin(kWifiSsid, kWifiPassword);
  mqttClient.setServer(kMqttHost, kMqttPort);
  mqttClient.setBufferSize(kTelemetryPayloadSize);
  mqttClient.setCallback(handleActuation);
  pinMode(kFanPin, OUTPUT);
  pinMode(kBuzzerPin, OUTPUT);
  pinMode(kStatusLed1Pin, OUTPUT);
  pinMode(kStatusLed2Pin, OUTPUT);
  setFan(false);
  setBuzzer(false);
  for (FuseInput &fuse : fuseInputs) {
    initializeFuseInput(fuse);
  }

  Serial.println();
  Serial.println("PredictFuse H1 board bring-up");
  Serial.println("Onboard LED blink test started");
  Serial.println("PredictFuse H2 DHT11 sensor polling started");
  Serial.println("PredictFuse H3 fuse-card polling started");
  Serial.println("PredictFuse H4 GPS parsing started");
  Serial.println("PredictFuse H5 telemetry started");
  Serial.println("PredictFuse H6 actuation started");
}

void loop() {
  const uint32_t now = millis();

  parseGpsData();
  maintainNetwork(now);

  if (now - lastBlinkMs >= kBlinkIntervalMs) {
    lastBlinkMs = now;
    digitalWrite(LED_BUILTIN, !digitalRead(LED_BUILTIN));
  }

  if (now - lastDhtPollMs >= kDhtPollIntervalMs) {
    lastDhtPollMs = now;
    readAndPrintZone(1, dhtZone1, zoneReadings[0]);
    readAndPrintZone(2, dhtZone2, zoneReadings[1]);
    readAndPrintZone(3, dhtZone3, zoneReadings[2]);
  }

  for (FuseInput &fuse : fuseInputs) {
    pollFuseInput(fuse, zoneReadings[fuse.zoneId - 1], now);
  }

  if (now - lastFuseStatusMs >= kFuseStatusIntervalMs) {
    lastFuseStatusMs = now;
    printFuseStatus(now);
  }

  if (now - lastGpsStatusMs >= kGpsStatusIntervalMs) {
    lastGpsStatusMs = now;
    printGpsStatus();
  }

  if (now - lastTelemetryMs >= kTelemetryIntervalMs) {
    lastTelemetryMs = now;
    char payload[kTelemetryPayloadSize];
    if (buildTelemetry(payload, sizeof(payload))) {
      queueTelemetry(payload);
      flushTelemetryQueue();
    }
  }
}
