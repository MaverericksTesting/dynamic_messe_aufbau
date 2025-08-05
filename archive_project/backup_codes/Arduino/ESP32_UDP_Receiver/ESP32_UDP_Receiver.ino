#include <WiFi.h>
#include <WiFiUdp.h>

const char* ssid = "TestNetz";
const char* password = "12345678";

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
  // Anzahl verbundener Clients anzeigen
  int numClients = WiFi.softAPgetStationNum();
  Serial.print("Verbunden Clients: ");
  Serial.println(numClients);

  // UDP-Paket prüfen
  int packetSize = udp.parsePacket();
  if (packetSize) {
    int len = udp.read(incomingPacket, sizeof(incomingPacket) - 1);
    if (len > 0) incomingPacket[len] = '\0';

    // Empfangene Zahl parsen
    int receivedNumber = atoi(incomingPacket);

    // Ausgabe untereinander
    Serial.println(receivedNumber);
  }

  delay(200); // etwas kürzer, für schnellere Reaktion
}
