#include <DFRobot_EC10.h>
#include <DFRobot_PH.h>
#include <OneWire.h>
#include <EEPROM.h>
#define EC_PIN A1
#define PH_PIN A2
// Pinout
int sensorInterrupt = 3;
int flowPin = 3;
int wl1Pin = 10;
int wl2Pin = 11;
int wl3Pin = 12;
int DS18S20_Pin = 8;
// temperature sensor init
OneWire ds(DS18S20_Pin);
// electrical conductivity init
DFRobot_EC10 ecSensor;
// ph sensor init
DFRobot_PH phSensor;
// flow meter variables
float calibrationFactor = 2.2;
volatile byte pulseCount;
float flowRate;
unsigned int flowMilliLitres;
unsigned long totalMilliLitres;
unsigned long oldFlowTime;
// sensor variables
float ph;
float ec;
float temp;
bool wl1;
bool wl2;
bool wl3;
// variables tracking last performance time
unsigned long prevTempTime;
unsigned long prevWLTime;
unsigned long prevECTime;
unsigned long prevPHTime;
unsigned long prevCommunicationTime;
unsigned long currentTime;
// set interval times
unsigned long tempTime = 450;
unsigned long WLTime = 450;
unsigned long ECTime = 450;
unsigned long PHTime = 450;
unsigned long fillTime = 1000;
unsigned long communicationTime = 1000;
void setup()
{
  Serial.begin(9600);
  ecSensor.begin();
  phSensor.begin();
  // init pins
  pinMode(wl1Pin, INPUT_PULLUP);
  pinMode(wl2Pin, INPUT_PULLUP);
  pinMode(wl3Pin, INPUT_PULLUP);
  pinMode(flowPin, INPUT);
  // init sensor values
  ph = getPH();
  ec = getEC();
  temp = getTemp();
  wl1 = getWL1();
  wl2 = getWL2();
  wl3 = getWL3();
  // init flow meter values
  pulseCount = 0;
  flowRate = 0.0;
  flowMilliLitres = 0;
  totalMilliLitres = 0;

  // init time values
  currentTime = millis();
  prevCommunicationTime = currentTime;
  prevTempTime = currentTime;
  oldFlowTime = currentTime;
  attachInterrupt(sensorInterrupt, pulseCounter, FALLING);
}
void pulseCounter()
{
  pulseCount++;
}
void loop()
{
  if (millis() < currentTime)
  {
    currentTime = millis();
    prevCommunicationTime = currentTime;
    prevTempTime = currentTime;
    oldFlowTime = currentTime;
    prevWLTime = currentTime;
    prevECTime = currentTime;
    prevPHTime = currentTime;
  }
  else
  {
    currentTime = millis();
  }
  handleFilling();

  // if time to check temperature, change the temperature variable
  if (currentTime - prevTempTime > tempTime)
  {
    prevTempTime = currentTime;
    temp = getTemp();
  }
  if (currentTime - prevWLTime > WLTime)
  {
    prevWLTime = currentTime;
    wl1 = getWL1();
    wl2 = getWL2();
    wl3 = getWL3();
  }
  if (currentTime - prevECTime > ECTime)
  {
    prevECTime = currentTime;
    getEC();
  }
  if (currentTime - prevPHTime > PHTime)
  {
    prevPHTime = currentTime;
    getPH();
  }
  // if time to communicate, send message to the pi
  if (currentTime - prevCommunicationTime > communicationTime)
  {
    prevCommunicationTime = currentTime;
    // format ph,ec,temp,wl1,wl2,wl3,flow
    Serial.print(ph);
    Serial.print(',');
    Serial.print(ec);
    Serial.print(',');
    Serial.print(temp);
    Serial.print(',');
    Serial.print(wl1);
    Serial.print(',');
    Serial.print(wl2);
    Serial.print(',');
    Serial.print(wl3);
    Serial.print(',');
    Serial.print(totalMilliLitres);
    Serial.print('\n');
    totalMilliLitres = 0;
  }
}
void handleFilling()
{
  if ((millis() - oldFlowTime) > fillTime) // Only process counters once per second  {
    // Disable the interrupt while calculating flow rate and sending the value to
    // the host
    detachInterrupt(sensorInterrupt);

  // Because this loop may not complete in exactly 1 second intervals we calculate
  // the number of milliseconds that have passed since the last execution and use
  // that to scale the output. We also apply the calibrationFactor to scale the output
  // based on the number of pulses per second per units of measure (litres/minute in
  // this case) coming from the sensor.
  flowRate = (pulseCount / (millis() - oldFlowTime)) / calibrationFactor;
  // flowRate = ((1000.0 / (millis() - oldFlowTime)) * pulseCount) / calibrationFactor;

  // Note the time this processing pass was executed. Note that because we've
  // disabled interrupts the millis() function won't actually be incrementing right
  // at this point, but it will still return the value it was set to just before
  // interrupts went away.
  oldFlowTime = millis();

  // Divide the flow rate in litres/minute by 60 to determine how many litres have
  // passed through the sensor in this 1 second interval, then multiply by 1000 to
  // convert to millilitres.
  flowMilliLitres = (flowRate / 60) * 1000;

  // Add the millilitres passed in this second to the cumulative total
  totalMilliLitres += flowMilliLitres;

  unsigned int frac;
  // Reset the pulse counter so we can start incrementing again
  pulseCount = 0;

  // Enable the interrupt again now that we've finished sending output
  attachInterrupt(sensorInterrupt, pulseCounter, FALLING);
}
float getPH()
{
  float voltage = analogRead(PH_PIN) / 1024.0 * 5000;
  // phSensor.calibration(voltage,temp);
  ph = phSensor.readPH(voltage, temp);
}
float getEC()
{
  float voltage = analogRead(EC_PIN) / 1024.0 * 5000;
  // ecSensor.calibration(voltage,temp);
  ec = ecSensor.readEC(voltage, temp);
}
float getTemp()
{
  // returns the temperature from one DS18S20 in DEG Celsius
  byte data[12];
  byte addr[8];
  if (!ds.search(addr))
  {
    // no more sensors on chain, reset search
    ds.reset_search();
    return -1000;
  }
  if (OneWire::crc8(addr, 7) != addr[7])
  {
    Serial.println("CRC is not valid!");
    return -1000;
  }
  if (addr[0] != 0x10 && addr[0] != 0x28)
  {
    Serial.print("Device is not recognized");
    return -1000;
  }
  ds.reset();
  ds.select(addr);
  ds.write(0x44, 1); // start conversion, with parasite power on at the end
  byte present = ds.reset();
  ds.select(addr);
  ds.write(0xBE); // Read Scratchpad
  for (int i = 0; i < 9; i++)
  { // we need 9 bytes
    data[i] = ds.read();
  }
  ds.reset_search();
  byte MSB = data[1];
  byte LSB = data[0];
  float tempRead = ((MSB << 8) | LSB); // using two's compliment
  float TemperatureSum = tempRead / 16;
  return TemperatureSum;
}
bool getWL1()
{
  return digitalRead(wl1Pin);
}
bool getWL2()
{
  return digitalRead(wl2Pin);
}
bool getWL3()
{
  return digitalRead(wl3Pin);
}
