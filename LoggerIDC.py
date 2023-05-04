########################################################################
# Simple custom logger class
# Author: Nathan Hayes
# Last Updated: 3/22/2023 - 3:00am

import time
import datetime
import os

########################################################################
# Class: LoggerIDC
# Disc: Basic logger function to write messages to an output file
#
# Functions:
#   __init__(self, sec)
#   timestamp(self)
# log(self, logStr)
# logData(self, d)
# logError(self, errorStr)
# getFileName(self)
# closeLog(self)
#


class LoggerIDC:

    # Initialize and create a new file to log to
    def __init__(self, fileName=None):
        # Create a new file name if one is not provided
        if fileName is None:
            path = os.path.dirname(os.path.realpath(__file__))
            print(path)
            curr = datetime.datetime.today().strftime('%Y-%m-%d_%H-%M-%S')
            self.name = "logs/"+str(curr)+"_log.txt"
        else:
            self.name = fileName

        # Open the file
        self.log = open(self.name, "w")

        # Log an opening statement
        self.log.write(
            "["+self.timestamp()+"] Opened Log File "+self.name+'\n')

    # Generates a timestamp string
    def timestamp(self):
        curr = datetime.datetime.today().strftime('%Y-%m-%d %H:%M:%S')
        return curr

    # Generic log message with timestamp
    def logStr(self, logStr):
        self.log.write("["+self.timestamp()+"] " +
                       logStr+' -- Written by logger\n')

    # Data log message with timestamp
    def logData(self, d):
        self.log.write("["+self.timestamp()+"] DATA: "+str(d)+"\n")

    # Error log message with timestamp and custom descriptor
    def logError(self, errorStr):
        self.log.write("["+self.timestamp()+"] ERROR: "+errorStr+"\n")

    # Return the file name
    def getFileName(self):
        return self.name

    # Close the logging file
    def closeLog(self):
        self.log.write("["+self.timestamp()+"] END RUN\n")
        self.log.close()
