########################################################################

# Main Application script for Automated Hydroponics Rack- IDC 2023
# Author: Avish Kandi
# Author: Nathan Hayes
# Last Updated: 5/3/2023 - 4:00pm
from flask import Flask, jsonify, render_template, request, send_from_directory
from flask_executor import Executor
from PeripheralControl_IDC import Relay, Motor, cleanupPins
from TimerIDC import durationToSec, TimerIDC
from AppManagerIDC import AppManagerIDC
import datetime
import time
import sys
import os
import subprocess

########################################################################

# Flask interface with website
app = Flask(__name__, template_folder='templates')
executor = Executor(app)

# Create system manager class
manager = AppManagerIDC()

# Temporary variables to be swapped out with Avish
wateringFrequency = 5
wateringDuration = 1
growCycleDuration = durationToSec(7, 0, 0, 0)
upperPHBound = 6
lowerPHBound = 4
upperECBound = 8
lowerECBound = 6
lowerTempBound = 20
nutrientRatio = 0.03
logFrequency = 4

# Init control peripheral pins
inflowValve = Relay(16)
dumpValve = Relay(17)
pHupPump = Motor(19,  20)
pHdownPump = Motor(22,  23)
nutrientPump = Motor(25,  27)
outflowPump = Motor(5, 6)

# Timers
mixTimer = TimerIDC(durationToSec(0, 0, 0, 30))
downTimer = TimerIDC(durationToSec(0, 0, wateringFrequency, 0))
wateringTimer = TimerIDC(durationToSec(0, 0, wateringDuration, 0))
logTimer = TimerIDC(3)
standbyTimer = TimerIDC(3)
growCycleTimer = TimerIDC(growCycleDuration)

# Error timeout timers
fillTimeout = TimerIDC(120)
outflowTimeout = TimerIDC(durationToSec(0, 0, 5, 0))
backflowTimeout = TimerIDC(durationToSec(0, 0, 1, 0))
mixTimeout = TimerIDC(durationToSec(0, 0, 10, 0))
serialTimeout = TimerIDC(30)

# Globals
dataJSON = None
print("Waiting for initial data")
while dataJSON == None:
    if manager.dataWaiting():
        dataJSON = manager.getData(True)

########################################################################

# Render Template
@app.route('/')
def index():
    return render_template('Index.html')

# Retrieve the data JSON packet for the website
@app.route('/data')
def dataToSite():
    # print(dataJSON)
    # print("------Got Data For Website---------")
    return manager.get_data_json()

# Shutdown the system
@app.route('/shutdown')
def shutdown():
    # manager.ser.close()
    manager.systemActive = False
    return "Serial port closed."

# Get settings from app as a single batch POST
@app.route('/save-settings', methods=['POST'])
def saveSetting():
    global wateringFrequency, wateringDuration, growCycleDuration, upperPHBound, lowerPHBound, upperECBound, lowerECBound, lowerTempBound, nutrientRatio, logFrequency

    wateringFrequency = request.form.get('watering_Frequency')
    if wateringFrequency:
        wateringFrequency = int(wateringFrequency)
    else:
        wateringFrequency = 0

    wateringDuration = int(request.form.get('watering_Duration'))
    growCycleDuration = int(request.form.get('growCycle_Duration'))
    upperPHBound = float(request.form.get('upper_PH'))
    lowerPHBound = float(request.form.get('lower_PH'))
    upperECBound = float(request.form.get('upper_EC'))
    lowerECBound = float(request.form.get('lower_EC'))
    lowerTempBound = float(request.form.get('lower_Temp'))
    nutrientRatio = float(request.form.get('nutrient_Ratio'))
    logFrequency = int(request.form.get('log_Frequency'))

    # save_settings_to_file_or_database(settings)
    return jsonify({"status": "success"})

# Take a Snapshot of the rack
@app.route('/snapshots/<path:filename>')
def serve_snapshot(filename):
    return send_from_directory('snapshots', filename)

# Take a Snapshot of the rack
@app.route('/take-snapshot')
def take_snapshot():
    timestamp = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
    snapshot_file = os.path.join('snapshots', f'snapshot_{timestamp}.png')
    cmd = f'fswebcam -r 640x480 --no-banner {snapshot_file}'

    try:
        subprocess.run(cmd, shell=True, check=True)
    except subprocess.CalledProcessError as e:
        return jsonify({'error': f'Error taking snapshot: {str(e)}'})

    return jsonify({'message': 'Snapshot saved', 'filename': f'snapshot_{timestamp}.png'})

# Start the system
@app.route('/start-system')
def startCycle():
    manager.toState('standby')
    return "System started", 200

# Stop the system
@app.route('/stop-system')
def manualStop():
    manager.toState('shutdown')
    return "System stopped", 200

########################################################################

def mainLoop():

    # Logic Variables
    cumulativeFlow = 0

    # Prime the Data JSON = manager.getData(True)

    # Start initial downtime timer
    downTimer.start()
    logTimer.start()
    standbyTimer.start()

    print(str(manager.dataJSON))
    # While system is active (can be turned off by @app.route(/shutdown))
    while (manager.systemActive):
        # state = 'shutdown'

        # Check for a serial message
        if manager.dataWaiting():
            serialTimeout.start()

            # Check whether we should formally log this one
            if logTimer.isFinished():
                logTimer.start()
                print("STATE: "+manager.state)
                dataJSON = manager.getData(True)
                print(manager.data)

            else:
                dataJSON = manager.getData(False)

        # If its been a while since we've read data, ERROR STATE
        elif (serialTimeout.isFinished()):
            text = "Lost Connection with Arduino: System Standby"
            manager.error(True, False, text, inflowValve, outflowPump)

        # Get easy-to-type names for data struct & state
        data = manager.data
        state = manager.state
        ############################################################
        # Standby for inactive reservoir
        if state == 'standby':

            if standbyTimer.isFinished():
                standbyTimer.start()

                # Check water level
                if not data["waterHigh"]:
                    inflowValve.OpenValve()
                    fillTimeout.start()
                    manager.toState('filling')

                # Check pH
                elif (not manager.waterOnly) and (
                    data["ph"] > upperPHBound or
                        data["ph"] < lowerPHBound):
                    manager.toState('conditioning')
                    mixTimer.start()
                    mixTimeout.start()

                # Check whether its time for a watering
                elif (downTimer.isFinished()):
                    manager.toState('watering')
                    outflowTimeout.start()
                    backflowTimeout.start()
                    outflowPump.setSpeed(100)
                    # Note: both timers are restarted at the same time
                    # to maintain proper cycle frequency
                    downTimer.start()
                    wateringTimer.start()

                else:

                    # Check temp sensor is working
                    if (data["temp"] < 0):
                        text = "Lost connection with temp probe: Check probe"
                        manager.error(False, False, text,
                                      inflowValve, outflowPump)

                    # Check heater is working
                    if (data["temp"] < lowerTempBound):
                        text = "Water temperature low: Check heater"
                        manager.error(False, False, text,
                                      inflowValve, outflowPump)

                    # Check ec
                    if (not manager.waterOnly) and (
                        data["ec"] > upperECBound or
                            data["ec"] < lowerECBound):
                        text = "EC out of range: changing to standby"
                        manager.error(False, False, text,
                                      inflowValve, outflowPump)

        ############################################################
        # Refilling the reservoir from the hose
        elif state == 'filling':

            # Add most recent flow count to cumulativeFlow
            cumulativeFlow = cumulativeFlow + data["flow"]

            # If bucket is full, move to conditioning
            if (bool(data["waterHigh"])):
                fillTimeout.abort()
                inflowValve.CloseValve()

                # If we don't need nutrients
                if (manager.waterOnly):
                    manager.toState('standby')

                # Check whether inflow was monitored
                elif (cumulativeFlow > 0):
                    # Add nutrients!
                    nutrientML = cumulativeFlow*nutrientRatio
                    nutrientMIN = nutrientML / 76
                    nutrientPump.runFor(100, nutrientMIN*60)
                    manager.toState('standby')

                # Inflow not monitored, ERROR STATE
                else:
                    text = "Flow meter disabled: Changing to freshwater watering"
                    manager.error(False, False, text, inflowValve, outflowPump)

            # Too long to fill, ERROR STATE
            elif (fillTimeout.isFinished()):
                text = "No fresh water: System Standby"
                manager.error(True, False, text, inflowValve, outflowPump)

        ############################################################
        # Conditioning pH of the reservoir
        elif state == 'conditioning':
            targetPH = (upperPHBound + lowerPHBound) / 2

            # If we've waited for the solution to mix
            if (mixTimer.isFinished()):
                mixTimer.start()

                # Calculate % error
                pHdiff = (data["ph"] - targetPH) / targetPH
                # pH is more than +5% off, add pH down
                if (data["ph"] > upperPHBound):
                    # run motor for % seconds
                    pHdownPump.runFor(100, 10*pHdiff)
                    print("pH down for "+str(10*pHdiff))

                # pH is more than -5% off, add pH up
                elif (data["ph"] < lowerPHBound):
                    # run motor for % seconds
                    pHupPump.runFor(100, -10*pHdiff)
                    print("pH up for "+str(-10*pHdiff))

                # pH is within tolerance, back to standby
                else:
                    manager.toState('standby')

                # Mixing is broken, ERROR STATE
                if (mixTimeout.isFinished()):
                    text = "Mixing incomplete: Changing to freshwater watering"
                    manager.error(False, True, text, inflowValve, outflowPump)
                    manager.toState('dumping')

        ############################################################
        # Pumping solution to rack
        elif state == 'watering':

            if data["waterLow"]:
                backflowTimeout.start()

            # If reservoir gets too low, stop pumping
            if not data["waterLow"]:
                outflowPump.brake()
                outflowTimeout.abort()

            # If the reservoir is at least half full, keep pumping
            elif (data["waterMid"]):
                outflowTimeout.start()
                outflowPump.setSpeed(75)

            # If the watering period is over, go back to standby
            if (wateringTimer.isFinished()):
                outflowPump.brake()
                manager.toState('standby')
                downTimer.start()

            # If the outflow timeout triggers, ERROR STATE
            if (outflowTimeout.isFinished()):
                text = "Outflow not working: System standby"
                manager.error(True, False, text, inflowValve, outflowPump)

            # If the backflow timeout triggers, ERROR STATE
            if (backflowTimeout.isFinished()):
                text = "Backflow low or blocked: Refilling reservoir"
                manager.error(False, False, text, inflowValve, outflowPump)
                downTimer.start()

        ############################################################
        # Dump solution out
        elif state == 'dumping':

            # If the reservoir is finally empty
            if not data["waterLow"]:
                manager.toState('filling')
                fillTimeout.start()
                inflowValve.OpenValve()
                dumpValve.CloseValve()
                outflowPump.brake()

            # Otherwise, keep dumping
            else:
                dumpValve.OpenValve()
                outflowPump.setSpeed(75)

        ############################################################
        # Limbo error state for severe plumbing issues
        elif state == 'error':
            # Do Nothing Here
            # manager.toState('error')
            dummy = True
            manager.systemActive = False

        ############################################################
        # Non-Active state controlled by the app
        elif state == 'shutdown':
            # Shutdown protocol
            dumpValve.CloseValve()
            inflowValve.CloseValve()
            outflowPump.brake()

        ############################################################
        # Default state jumps back to standby
        else:
            # Default
            dumpValve.CloseValve()
            inflowValve.CloseValve()
            outflowPump.brake()
            manager.toState('standby')

    # System deactivated, cleanup everything
    # Set GPIOs off
    cleanupPins()
    manager.closeLog()

    sys.exit("Exiting after full shutdown")

########################################################################

# Begin server
@app.before_first_request
def run_main_loop():
    executor.submit(mainLoop)


app.run(debug=True, host='0.0.0.0')
