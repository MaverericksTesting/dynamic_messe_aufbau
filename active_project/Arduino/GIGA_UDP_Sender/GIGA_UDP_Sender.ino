#include <WiFi.h>
#include <WiFiUdp.h>

const char* ssid     = "Dynamic_Messestand";      // ESP32 SSID
const char* password = "Star!testing";      // ESP32 Passwort

WiFiUDP udp;
const char* esp32_ip = "192.168.4.1";   // IP des ESP32 SoftAP
const int udpPort = 4210;

int numberToSend = 1;

void setup() {
  Serial.begin(115200);
  WiFi.begin(ssid, password);

  Serial.print("Verbinde mit WiFi");
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("\n✅ WiFi verbunden!");
  Serial.print("Meine IP: ");
  Serial.println(WiFi.localIP());

  Serial.print("Verbunden mit SSID: ");
  Serial.println(WiFi.SSID());
}

void loop() {
  char msg[5];
  sprintf(msg, "%d", numberToSend);

  udp.beginPacket(esp32_ip, udpPort);
  udp.write(msg);
  udp.endPacket();

  Serial.print("Gesendet: ");
  Serial.println(msg);

  numberToSend++;
  if (numberToSend > 10) numberToSend = 1;

  delay(2000);
}
