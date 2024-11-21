#include <WiFiNINA.h> //Gestión de conexión wifi del módulo MKR1010
#include <ArduinoMqttClient.h> //PubSubClients no soporta TLS/SSL
#include <Arduino_MKRENV.h>    //Librería para el MKR ENV Shield

// Configuración WiFi - No compatible con 5G
const char* ssid = "S6 de Mario"; //Nombre de la red
const char* password = "moscasmelosas"; //contraseña

WiFiClient wifiClient;
MqttClient client(wifiClient);

// Configuración MQTT
const char broker_mqtt[] = "broker.hivemq.com";
const int port_mqtt = 1883;

// Topics (Están de ejemplo)
const char publish_topic_L[] = "/LightningMcHouse/measurements/light";
const char publish_topic_T[] = "/LightningMcHouse/measurements/temperature";
const char publish_topic_D[] = "/LightningMcHouse/measurements/distance";

// Pines del sensor ultrasónico
const int trigPin = 6; //Pin digital para Trig
const int echoPin = 7; //Pin digital para Echo 

// Función para re-conectar al WiFi
void setup_wifi() {
  Serial.println("Connecting to WiFi...");
  WiFi.begin(ssid, password);

  while (WiFi.status() != WL_CONNECTED) {
    delay(3000); //Reintentar conexión cada 3 segundos
    Serial.print(".");

  }

  Serial.println("\nKachao! WiFi conected!");
  Serial.print("IP: ");
  Serial.println(WiFi.localIP());
}

// Función para re-conectar al broker MQTT
void reconnect (){
  Serial.print("Attempting to connect to the MQTT broker: ");
  Serial.println(broker_mqtt);
  while (!client.connect(broker_mqtt, port_mqtt)) {
    Serial.print("MQTT connection failed. Error code = ");
    Serial.println(client.connectError());
    delay(3000); //Intentar de nuevo en 3 segundos

  }
  Serial.println("You're connected to the MQTT broker!");
  Serial.println();
}
// Hat y pines de ultrasonido
void setup() {
  Serial.begin(9600);
  while (!Serial);

  setup_wifi();

  if (!ENV.begin()) {
    Serial.println("Error initializing MKR ENV Shield");
    while (1); // Bloquear el programa si falla
  }
  Serial.println("MKR ENV Shield initialized");

  pinMode(trigPin, OUTPUT);
  pinMode(echoPin, INPUT);
}

float medirDistancia() {
  digitalWrite(trigPin, LOW);
  delayMicroseconds(2);
  digitalWrite(trigPin, HIGH);
  delayMicroseconds(10);
  digitalWrite(trigPin, LOW);

  long duration = pulseIn(echoPin, HIGH);
  float distance = duration * 0.034 / 2;
  return distance;
}

void loop() {
  if (!client.connected()) {
    reconnect();
  }

  client.poll(); // Procesa mensajes entrantes

  // Leer sensores del MKR ENV Shield
  float lux = ENV.readIlluminance();
  float temp = ENV.readTemperature();
  float dist = medirDistancia();

  Serial.print("Light intensity: ");
  Serial.println(lux);
  Serial.print("Temperature: ");
  Serial.println(temp);
  Serial.print("Distance: ");
  Serial.println(dist);

  // Publicar datos
  client.beginMessage(publish_topic_L);
  client.print(lux);
  client.endMessage();

  client.beginMessage(publish_topic_T);
  client.print(temp);
  client.endMessage();

  client.beginMessage(publish_topic_D);
  client.print(dist);
  client.endMessage();

  delay(5000); // Pausa de 5 segundo antes de la siguiente lectura
}


