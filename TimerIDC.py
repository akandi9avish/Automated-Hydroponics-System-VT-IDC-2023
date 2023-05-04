########################################################################
# Simple custom duration timer class
# Author: Nathan Hayes
# Last Updated: 3/22/2023 - 3:00am
import time

########################################################################
# Return a duration in days/hrs/min/sec to total seconds


def durationToSec(days, hours, minutes, seconds):
    totalHrs = hours + (days*24)
    totalMin = minutes + (totalHrs*60)
    totalSec = seconds + (totalMin*60)
    return totalSec

########################################################################
# Class: TimerIDC
# Disc: Basic timer function to determine when a certain amount of time
# has elapsed. All time values are in seconds
#
# Functions:
#   __init__(self, sec)
#   start(self)
# abort(self)
# isFinished(self)
# setDuration(self, sec)
#


class TimerIDC:

    # Initialize timer with a set number of seconds
    def __init__(self, sec):
        self.duration = sec
        self.active = False
        self.startTime = time.time()
        self.endTime = 0

    # Calculates the start and end times and begins the timer
    def start(self):
        self.active = True
        self.startTime = time.time()
        self.endTime = self.startTime + self.duration

    # Kills the timer until it is (re)started
    def abort(self):
        self.active = False

    # Returns true if the timer has passed its duration
    def isFinished(self):
        currTime = time.time()
        return (currTime > self.endTime) and (self.active)

    # Change the intended duration of the timer
    # NOTE: should only be called BEFORE start(), calling after start()
    # 		will not change the duration of the running timer
    def setDuration(self, sec):
        self.duration = sec
