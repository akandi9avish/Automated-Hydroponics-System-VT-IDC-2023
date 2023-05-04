########################################################################
# Validation script for Artre's Flow Validation
# Author: Nathan Hayes
# Last Updated: 3/22/2023 - 3:00am

from flask import Flask, jsonify, render_template
from PeripheralControl import Relay, Motor
import TimerIDC
import AppManagerIDC

outflowPump = Motor(13, 14, 15)
inflowValve = Relay(16)
testTimer = TimerIDC(60)
man = AppManagerIDC()

########################################################################


def inflowRateTest(sec):
    inflowValve.OpenValve()
    testTimer.start()

    cumulativeFlow = 0

    while not testTimer.isFinished():

        if man.ser.in_waiting:
            dataJSON = manager.getData()
            data = manager.data

        cumulativeFlow = cumulativeFlow + data["flow"]

    inflowValve.CloseValve()

    print(cumulativeFlow)


def outflowRateTest(sec):
    outflowPump.runFor(100, sec)


########################################################################
# if __name__ == '__main__':

inflowRateTest(60)
outflowRateTest(60)
