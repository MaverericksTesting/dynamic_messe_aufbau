#include <WiFi.h>
#include <WiFiUdp.h>

const char* ssid = "Dynamic_Messestand";
const char* password = "Star!testing";

WiFiUDP udp;
const int udpPort = 4210;

char incomingPacket[255];

void setup() {
  Serial.begin(115200);

  WiFi.softAP(ssid, password);
  IPAddress myIP = WiFi.softAPIP();
  Serial.print("✅ ESP32 AP gestartet! IP: ");
  Serial.println(myIP);

  udp.begin(udpPort);
  Serial.println("Warte auf UDP Nachrichten...");
}

void loop() {
  // Anzahl verbundener Clients anzeigen (nur alle 5 Sekunden)
  static unsigned long lastClientCheck = 0;
  if (millis() - lastClientCheck > 5000) {
    int numClients = WiFi.softAPgetStationNum();
    Serial.print("Clients: ");
    Serial.println(numClients);
    lastClientCheck = millis();
  }

  // UDP-Paket prüfen
  int packetSize = udp.parsePacket();
  if (packetSize) {
    int len = udp.read(incomingPacket, sizeof(incomingPacket) - 1);
    if (len > 0) incomingPacket[len] = '\0';

    // Empfangene Zahl parsen
    int receivedNumber = atoi(incomingPacket);

    // Direkte Weiterleitung an Mini PC (Python GUI)
    // Format: "SIGNAL:X" für bessere Erkennung
    Serial.print("SIGNAL:");
    Serial.println(receivedNumber);
  }

  delay(50); // Schnellere Reaktion für GUI
}
