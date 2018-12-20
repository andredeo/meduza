/**************************************************************************************************
   Sensor com fio para a coleta de grandezas de transdutores Grove utilizando o Pacote Radiuino
 *                                                                                                *
   Sound Sensor
   Air Quality Sensor
   Temperature & Humidity sensor pro (DHT22)
 *                                                                                                *
                                                                  Raphael Montali da Assumpção
 *************************************************************************************************/

/*
   Inclusão de Bibliotecas
*/
#include "DHT.h"
#include"Arduino.h"
#include "TimerOne.h"


/*
   Inclusões da biblioteca AirQuality para não ter de usar o timer somente para ela
*/

#include"AirQuality_no_timer.h"
AirQuality_no_timer airqualitysensor;
int current_quality = -1; // Variável para a qualidade do Ar
unsigned long acumulaQualidade = 0; // Utilizado para média do som por segundo
int mediaQualidade = 0;

int luminosidade;

int pinos[8] = {22, 24, 26, 28, 30, 32, 34, 36};
int cooler = 12;
int buzzer = 14;
/*
   Definições
*/

#define AirQualityPin A0  // Pino do sensor de qualidade do Ar
#define SoundSensorPin A1 //ìno do sensor de Som
#define LDR A12 //ìno do sensor de Som
#define DHTPIN 4  // Pino do sensor de Temperatura e Umidade.

/*
   Configurações do sensor
*/
const int endereco = 1; //Endereco do sensor

byte PacoteEntrada[52]; // Inicializacao do pacote de entrada
byte PacoteSaida[52]; // Inicializacao do pacote de saida


float temperatura;  // Variável que armazena a Temperatura
float umidade; //Variável que armazena a Umidade

const int trigPin = 15; //Trigger do sensor ultrassom
const int echoPin = 16; //Echo do sensor ultrassom

int distancia;

unsigned long acumulaSom = 0; // Utilizado para média do som por segundo

int mediaSom = 0;
int maxSom = 0;
int minSom = 1024;
int maxSom_last = 0;
int minSom_last = 0;

unsigned long previousMillis1 = 0; // Utilizado para controle do tempo
const long interval1 = 1000;           // interval(milliseconds)(10 ms)

unsigned long previousMillis2 = 0; // Utilizado para controle do tempo
const long interval2 = 2000;           // interval(milliseconds)(2 s)

unsigned long previousMillis3 = 0; // Utilizado para controle do tempo
const long interval3 = 5000;           // interval(milliseconds)(1 min, 60000)

unsigned long previousMillis4 = 0; // Utilizado para controle do tempo
const long interval4 = 300000;           // interval(milliseconds) (5 min, 300000)

unsigned long previousMillis5 = 0; // Utilizado para controle do tempo
const long interval5 = 10000;           // interval(milliseconds) (10 segundos, 10000)

unsigned long currentMillis1;  // Utilizado para controle do tempo
unsigned long currentMillis2;  // Utilizado para controle do tempo
unsigned long currentMillis3;  // Utilizado para controle do tempo
unsigned long currentMillis4;  // Utilizado para controle do tempo
unsigned long currentMillis5;  // Utilizado para controle do tempo

//unsigned long currentMillis2;  // Utilizado para controle do tempo


//AirQuality airqualitysensor;

DHT dht(DHTPIN, DHT22);

void setup() {
  // inicializacao da serial
  Serial.begin(9600);

  pinMode(trigPin, OUTPUT);
  pinMode(echoPin, INPUT);

  for (int x = 0; x < 8; x++) {
    pinMode(pinos[x], OUTPUT);
  }

  for (int x = 0; x < 8; x++) {
    digitalWrite(pinos[x], HIGH);
    delay(500);
  }

  for (int x = 0; x < 8; x++) {
    digitalWrite(pinos[x], LOW);
    delay(500);
  }

  //Serial.println("antes do init");

  airqualitysensor.init(14); //  Precisa ser inicializado antes de ativar qualquer rotina de timer ex.( TimerOne)
  previousMillis2 = millis();
  //Serial.println("depois do init");
  umidade = dht.readHumidity();
  temperatura = dht.readTemperature();

  for (int x = 0; x < 8; x++) {
    digitalWrite(pinos[x], HIGH);
    delay(1);
  }

  for (int x = 0; x < 8; x++) {
    digitalWrite(pinos[x], LOW);
    delay(1);
  }

  pinMode(cooler, OUTPUT);
  digitalWrite(cooler, LOW);

  pinMode(buzzer, OUTPUT);
  digitalWrite(buzzer, LOW);

}

void loop() {
  // put your main code here, to run repeatedly:

  if (Serial.available() == 52)
  {
    for (int j = 0; j < 52; j++)
    {
      PacoteSaida[j] = 0;
      PacoteEntrada[j] = Serial.read();  /* Pacote é o nosso buffer global */
      delay(1); // Delay de 1ms para voltar a ler a serial
    }

    //dist();

    //if((PacoteEntrada[8] == endereco)&&(PacoteEntrada[7] == 0)&&(PacoteEntrada[9] == 0))
    if (PacoteEntrada[8] == endereco)
    {

      PacoteSaida[0] = PacoteEntrada[2];
      PacoteSaida[1] = PacoteEntrada[3];

      PacoteSaida[8] = PacoteEntrada[10];
      PacoteSaida[10] = PacoteEntrada[8];

      //PacoteSaida[16] = 0;
      PacoteSaida[17] = (byte) ((int)(mediaQualidade) / 256);
      PacoteSaida[18] = (byte) ((int)(mediaQualidade) % 256);

      //PacoteSaida[19] = 0;
      //PacoteSaida[20] = (byte) ((int)(airqualitysensor.vol_standard) / 256);
      //PacoteSaida[21] = (byte) ((int)(airqualitysensor.vol_standard) % 256);
      PacoteSaida[20] = (byte) ((int)(analogRead(A0)) / 256);
      PacoteSaida[21] = (byte) ((int)(analogRead(A0)) % 256);

      PacoteSaida[22] = 0;
      PacoteSaida[23] = (byte) ((int)(mediaSom) / 256);
      PacoteSaida[24] = (byte) ((int)(mediaSom) % 256);

      PacoteSaida[25] = 0;
      PacoteSaida[26] = (byte) ((int)(maxSom_last) / 256);
      PacoteSaida[27] = (byte) ((int)(maxSom_last) % 256);

      PacoteSaida[28] = 0;
      PacoteSaida[29] = (byte) ((int)(minSom_last) / 256);
      PacoteSaida[30] = (byte) ((int)(minSom_last) % 256);

      PacoteSaida[16] = (byte) ((int)(distancia) / 256);
      PacoteSaida[19] = (byte) ((int)(distancia) % 256);

      PacoteSaida[31] = (byte) ((int)(luminosidade) / 256);
      PacoteSaida[32] = (byte) ((int)(luminosidade) % 256);

      //Temperatura no pacote (IO0)
      if (temperatura < 0) {
        PacoteSaida[34] = 1; // Sinal (1 é negativo) no byte 34
      }
      else {
        PacoteSaida[34] = 0; // Sinal (0 é positivo) no byte 34
      }
      PacoteSaida[35] = (byte) ((int)(temperatura * 10) / 256); // Valor inteiro no byte 35
      PacoteSaida[36] = (byte) ((int)(temperatura * 10) % 256); // Resto da divisão no byte 36

      //Umidade no pacote(IO1)
      PacoteSaida[37] = 0; // Pode ser utilizado para indicar o tipo de sensor no byte 37
      PacoteSaida[38] = (byte) ((int)(umidade * 10) / 256); // Valor inteiro no byte 38
      PacoteSaida[39] = (byte) ((int)(umidade * 10) % 256); // Resto da divisão no byte 39

      // Byte 40 aciona o pino 22
      if (PacoteEntrada[40] == 1) {
        digitalWrite(pinos[0], HIGH);
        PacoteSaida[40] = 1;
      }
      else {
        digitalWrite(pinos[0], LOW);
        PacoteSaida[40] = 0;
      }

      // Byte 41 aciona o pino 24
      if (PacoteEntrada[41] == 1) {
        digitalWrite(pinos[1], HIGH);
        PacoteSaida[41] = 1;
      }
      else {
        digitalWrite(pinos[1], LOW);
        PacoteSaida[41] = 0;
      }

      // Byte 42 aciona o pino 26
      if (PacoteEntrada[42] == 1) {
        digitalWrite(pinos[2], HIGH);
        PacoteSaida[42] = 1;
      }
      else {
        digitalWrite(pinos[2], LOW);
        PacoteSaida[42] = 0;
      }

      // Byte 43 aciona o pino 28
      if (PacoteEntrada[43] == 1) {
        digitalWrite(pinos[3], HIGH);
        PacoteSaida[43] = 1;
      }
      else {
        digitalWrite(pinos[3], LOW);
        PacoteSaida[43] = 0;
      }

      // Byte 44 aciona o pino 30
      if (PacoteEntrada[44] == 1) {
        digitalWrite(pinos[4], HIGH);
        PacoteSaida[44] = 1;
      }
      else {
        digitalWrite(pinos[4], LOW);
        PacoteSaida[44] = 0;
      }

      // Byte 45 aciona o pino 32
      if (PacoteEntrada[45] == 1) {
        digitalWrite(pinos[5], HIGH);
        PacoteSaida[45] = 1;
      }
      else {
        digitalWrite(pinos[5], LOW);
        PacoteSaida[45] = 0;
      }

      // Byte 46 aciona o pino 34
      if (PacoteEntrada[46] == 1) {
        digitalWrite(pinos[6], HIGH);
        PacoteSaida[46] = 1;
      }
      else {
        digitalWrite(pinos[6], LOW);
        PacoteSaida[46] = 0;
      }

      // Byte 47 aciona o pino 36
      if (PacoteEntrada[47] == 1) {
        digitalWrite(pinos[7], HIGH);
        PacoteSaida[47] = 1;
      }
      else {
        digitalWrite(pinos[7], LOW);
        PacoteSaida[47] = 0;
      }

      // Byte 48 - liga todos os LEDs
      if (PacoteEntrada[48] == 1) {
        for (int i = 0; i < 8; i++) {
          digitalWrite(pinos[i], HIGH);
        }

        for (int j = 40; j <= 48; j++) {
          PacoteSaida[j] = 1;
        }
      }

      // Byte 49 aciona o pino 12 (cooler)
      if (PacoteEntrada[49] == 1) {
        digitalWrite(cooler, HIGH);
        PacoteSaida[49] = 1;
      }
      else {
        digitalWrite(cooler, LOW);
        PacoteSaida[49] = 0;
      }

      // Byte 50 aciona o pino 14 (buzzer)
      if (PacoteEntrada[50] == 1) {
        digitalWrite(buzzer, HIGH);
        PacoteSaida[50] = 1;
      }
      else {
        digitalWrite(buzzer, LOW);
        PacoteSaida[50] = 0;
      }



      //escrevendo o pacote de saída na Serial.
      for (int k = 0; k < 52; k++)
      {
        Serial.write(PacoteSaida[k]);
      }

    }

  }

  currentMillis1 = millis();
  currentMillis2 = millis();
  currentMillis3 = millis();
  currentMillis4 = millis();
  currentMillis5 = millis();
  //currentMillis2 = millis();

  if (currentMillis1 - previousMillis1 >= interval1) {

    long sum = 0;
    for (int i = 0; i < 32; i++)
    {
      sum += analogRead(SoundSensorPin);
    }

    sum >>= 5;

    if (sum < minSom) {
      minSom = sum;
    }
    if (sum > maxSom) {
      maxSom = sum;
    }

    acumulaSom += sum;
    previousMillis1 = currentMillis1;
  }

  if (currentMillis2 - previousMillis2 >= interval2) {

    /*
       Sensor de qualidade do ar
    */
    airqualitysensor.last_vol = airqualitysensor.first_vol;
    airqualitysensor.first_vol = analogRead(A0);
    airqualitysensor.timer_index = 1;
    //Serial.println(analogRead(A0));

    previousMillis2 = currentMillis2;
  }

  if (currentMillis3 - previousMillis3 >= interval3) {

    umidade = dht.readHumidity();
    temperatura = dht.readTemperature();
    luminosidade = 1023 - analogRead(LDR);
    luminosidade = map(luminosidade, 0, 1023, 0, 100);
    //Serial.println(umidade);
    //Serial.println(temperatura);
    //Serial.println(luminosidade);

    previousMillis3 = currentMillis3;
  }

  if (currentMillis4 - previousMillis4 >= interval4) {

    mediaSom = acumulaSom / 30000;
    minSom_last = minSom;
    maxSom_last = maxSom;

    //    Serial.print(minSom_last);
    //    Serial.print(";");
    //    Serial.print(maxSom_last);
    //    Serial.print(";");
    //    Serial.println(mediaSom);

    acumulaSom = 0;
    maxSom = 0;
    minSom = 1024;

    mediaQualidade = int(acumulaQualidade / 1.50); //Já está multiplocado por 100

    previousMillis4 = currentMillis4;
  }


  if (currentMillis5 - previousMillis5 >= interval5) {

    digitalWrite(trigPin, LOW);
    delayMicroseconds(2);
    digitalWrite(trigPin, HIGH);
    delayMicroseconds(10);
    digitalWrite(trigPin, LOW);
    unsigned long duracao = pulseIn(echoPin, HIGH);

    distancia = duracao / 58;
    //Serial.println(distancia);

    previousMillis5 = currentMillis5;
  }



  current_quality = airqualitysensor.slope();
  if (current_quality >= 0)// if a valid data returned.
  {
    //Serial.println(acumulaQualidade);
    acumulaQualidade = current_quality;
    //      if (current_quality==0)
    //          Serial.println("High pollution! Force signal active");
    //      else if (current_quality==1)
    //          Serial.println("High pollution!");
    //      else if (current_quality==2)
    //          Serial.println("Low pollution!");
    //      else if (current_quality ==3)
    //          Serial.println("Fresh air");
  }

  Serial.flush();
}

//Serial.flush();


//void dist() {
//  digitalWrite(trigPin, LOW);
//  delayMicroseconds(2);
//  digitalWrite(trigPin, HIGH);
//  delayMicroseconds(10);
//  digitalWrite(trigPin, LOW);
//  unsigned long duracao = pulseIn(echoPin, HIGH);
//
//  distancia = duracao / 58;
//}

