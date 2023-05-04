########################################################################
# App Management class containing logic variables, logging capabilities,
# and some other auxilary functions such as serial reading
# Author: Nathan Hayes
# Last Updated: 3/22/2023 - 3:00am

import time
import serial
import json
from PeripheralControl_IDC import Motor, Relay
from TimerIDC import TimerIDC
from LoggerIDC import LoggerIDC

########################################################################
# Class: AppManagerIDC
# Disc: A management data struct with baked-in functions for certain
#       edge conditions and errors
#
# Functions:
#   __init__(self, sec)
#   toState(self, newState)
#   error(self, suspend, freshOnly, errMsg)
#   getData(self)
#   closeLog(self)
#   dataWaiting(self)
#


class AppManagerIDC:

    # Initialize logic variables, logger, and serial port
    def __init__(self):
        self.state = 'standby'
        self.errorFlag = False
        self.errorText = ""
        self.systemActive = True
        self.waterOnly = False
        self.data = None
        self.dataJSON = None
        self.debug = False
        self.log = LoggerIDC()
        self.ser = serial.Serial('/dev/ttyACM0', 9600, timeout=1)

    # Simple function to change state & log edge
    def toState(self, newState):
        self.state = newState
        string = "Transitioned to "+str(newState)+" mode"
        print(string)
        self.log.logStr(string)

    # Function to record and error and adjust accordingly.
    # Suspend: Boolean for suspending the state into a permanent limbo
    # freshOnly: Boolean for changing to freshwater only mode
    def error(self, suspend, freshOnly, errMsg, valve, motor):
        valve.CloseValve()
        motor.brake()
        self.errorFlag = True
        self.errorText = errMsg
        self.log.logError(errMsg)
        print(errMsg)

        # Check whether to suspend the entire system
        if suspend:
            self.state = 'error'
        else:
            self.state = 'standby'

        # Check whether to move to freshwater mode
        if freshOnly:
            self.waterOnly = True

        # Log the error in the log file
        self.log.logError(errMsg)

    # Query serial port for data packet, convert to & from JSON
    def getData(self, log):

        tempJSON = None

        # Read entire string
        while self.ser.in_waiting:
            data = self.ser.readline().decode().strip().split(',')
            if len(data) == 7:
                ph = data[0]
                ec = data[1]
                temp = data[2]
                wl1 = data[3]  # high
                wl2 = data[4]  # med
                wl3 = data[5]  # low
                flow = str(int(data[6]))
                tempJSON = json.dumps({"ph": str(ph), "ec": str(ec), "temp": str(temp),
                                       "waterHigh": str(wl1), "waterMid": str(wl2), "waterLow": str(wl3),
                                      "flow": str(flow)})
        """
        ph = 7.0
        ec = 100
        temp = 72
        wl1 = 0
        wl2 = 1
        wl3 = 1
        flow = 0
        """
        if not tempJSON == None:
            print(tempJSON)
            self.dataJSON = tempJSON

            # Convert individual args to JSON and store
            # self.dataJSON = jsonify(ph=ph, ec=ec, temp=temp,
            #                    waterHigh=wl1, waterMid=wl2, waterLow=wl3,
            #                        flow=flow)
            # Also obtain JSON as a python dictionary
            self.data = json.loads(self.dataJSON)
            for item in self.data:
                self.data[item] = float(self.data[item])

            # Log the data into a log file
            if log:
                self.log.logData(self.data)

        # Cough up the JSON to the main function so it can be seen by
        # the website
        return self.dataJSON

    # getter for jason data
    def get_data_json(self):
        return self.dataJSON

    # Close up the file
    def closeLog(self):
        self.log.closeLog()

    # Serial Status Access Method
    def dataWaiting(self):
        return self.ser.in_waiting

    def fetchData(self):
        return self.dataJSON
