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
4. Set up your Arduino with the required sensors and actuators, and upload the appropriate sketch.

5. Run the Flask app:
   ```
   python main.py
   ```
6. Access the web interface by navigating to `http://localhost:5000` in your web browser.

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
