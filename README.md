# Automated Hydroponics Rack - IDC 2023

Automated Hydroponics Rack is a system designed to manage and control a hydroponic rack using a web interface. This system monitors and adjusts water levels, pH, nutrient levels, temperature, and other parameters to ensure optimal plant growth. It is based on Flask web framework and interfaces with Arduino for hardware control.

## Features

- Monitors and adjusts water levels
- Monitors and adjusts pH levels
- Monitors and adjusts nutrient levels
- Monitors and adjusts temperature
- Web interface to control and monitor the system
- Snapshot functionality to take pictures of the rack
- Error handling and system shutdown in case of failures

## Requirements

- Python 3
- Flask
- Flask-Executor
- Arduino with appropriate sensors and actuators
- DFRobot EC10 (electrical conductivity) sensor
- DFRobot PH sensor
- DS18S20 (temperature) sensor
- OneWire library for temperature sensor
- EEPROM library for storing calibration data
- Flow meter for monitoring water flow

## Arduino Pin Connections

- EC sensor: A1
- PH sensor: A2
- Flow meter: Digital pin 3 (interrupt pin)
- Water level sensor 1: Digital pin 10
- Water level sensor 2: Digital pin 11
- Water level sensor 3: Digital pin 12
- Temperature sensor: Digital pin 8

## Installation

1. Clone this repository:
   ```
   git clone https://github.com/akandi9avish/Automated-Hydroponics-System-VT-IDC-2023
   ```
2. Change to the repository directory:
   ```
   cd automated-hydroponics-rack
   ```
3. Install required dependencies:
   ```
   pip install -r requirements.txt
   ```
4. Set up your Arduino with the required sensors and actuators, and upload the provided Arduino sketch.

5. Run the Flask app:
   ```
   python main.py
   ```
6. Access the web interface by navigating to `http://localhost:5000` in your web browser.

## Arduino Setup and Code Explanation

The Arduino section of the Automated Hydroponics Rack project is responsible for monitoring and managing the hydroponic system's sensors and actuators. It communicates with the Flask server to send and receive data on the system's parameters.

### Sensors and Actuators

The following sensors and actuators are used in the Arduino setup:

1. DFRobot EC10 (electrical conductivity) sensor: Measures the electrical conductivity of the water in the hydroponic system.
2. DFRobot PH sensor: Measures the pH level of the water in the hydroponic system.
3. DS18S20 (temperature) sensor: Monitors the temperature of the water in the hydroponic system.
4. Flow meter: Monitors the flow of water through the hydroponic system.
5. Water level sensors: Three water level sensors are used to measure the water levels in the hydroponic system.

### Libraries

The following libraries are required for the Arduino code:

1. `<DFRobot_EC10.h>`: Library for the DFRobot EC10 sensor.
2. `<DFRobot_PH.h>`: Library for the DFRobot PH sensor.
3. `<OneWire.h>`: Library for the DS18S20 temperature sensor.
4. `<EEPROM.h>`: Library for storing calibration data.

### Pin Connections

The following pins are used for connecting the sensors and actuators to the Arduino:

- EC sensor: A1
- PH sensor: A2
- Flow meter: Digital pin 3 (interrupt pin)
- Water level sensor 1: Digital pin 10
- Water level sensor 2: Digital pin 11
- Water level sensor 3: Digital pin 12
- Temperature sensor: Digital pin 8

### Code Explanation

The Arduino code is responsible for reading data from the various sensors, processing it, and sending it to the Flask server. The main functions in the Arduino code are as follows:

1. `setup()`: Initializes the sensors, actuators, and pins, and sets initial values for variables.
2. `loop()`: The main loop that runs continuously, reading data from the sensors, processing it, and sending it to the Flask server.
3. `pulseCounter()`: Interrupt function to count pulses from the flow meter.
4. `handleFilling()`: Function to handle water filling in the hydroponic system based on the flow meter readings.
5. `getPH()`: Function to read the pH level from the PH sensor.
6. `getEC()`: Function to read the electrical conductivity from the EC sensor.
7. `getTemp()`: Function to read the temperature from the DS18S20 temperature sensor.
8. `getWL1()`, `getWL2()`, and `getWL3()`: Functions to read the water levels from the three water level sensors.

The main loop (`loop()`) is responsible for calling the functions to read and process data from the sensors at specified intervals, and sending the processed data to the Flask server in a formatted string via the serial communication.

The Arduino code uses interrupts to handle the flow meter readings accurately and efficiently. The flow meter's pulses are counted in the `pulseCounter()` function, which is triggered by the falling edge of the pulse signal. The flow rate and total milliliters of water are calculated in the `handleFilling()` function.

The temperature, pH, electrical conductivity, and water level readings are obtained from their respective functions, which use the relevant libraries and functions to read data from the sensors.

Finally, the processed data is sent to the Flask server via serial communication in a formatted string containing the values of pH, electrical conductivity, temperature, water levels, and flow rate.

## Usage

Once the server is running, you can access the web interface to control and monitor the hydroponic rack. The interface allows you to:

- Start and stop the system
- Set watering frequency, duration, and other parameters
- Monitor water levels, pH, nutrient levels, and temperature
- Take snapshots of the rack
- Shutdown the system in case of errors or failures

## API Endpoints

- `/`: Render the main template
- `/data`: Retrieve the data JSON packet for the website
- `/shutdown`: Shutdown the system
- `/save-settings`: Save settings from the app as a single batch POST
- `/snapshots/<path:filename>`: Serve a snapshot of the rack
- `/take-snapshot`: Take a snapshot of the rack
- `/start-system`: Start the system
- `/stop-system`: Stop the system

## Authors

- Avish Kandi
- Nathan Hayes

## License

This project is licensed under the Open Source License.