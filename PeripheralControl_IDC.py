########################################################################
# Classes for controlled peripherals (relays & motor controllers)
# Author: Nathan Hayes
# Last Updated: 3/22/2023 - 3:00am
import RPi.GPIO as GPIO
import time
import threading

########################################################################
# Class: Relay
# Disc: Class to control the hardware relay attached to the flow control
#       valve. Note that the valve should be hooked to the relay in an
#       active-high configuration (i.e GPIO.HIGH = valve open)
#
# Functions:
#   __init__(self, pin)
#   OpenValve(self)
#   CloseValve(self)
#


class Relay:

    # Initialize a Relay on a Pin
    def __init__(self, pin):
        self.pin = pin
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        GPIO.setup(pin, GPIO.OUT)

    # Open the valve (set IO high)
    def OpenValve(self):
        GPIO.output(self.pin, GPIO.HIGH)

    # Close the valve (set IO low)
    def CloseValve(self):
        GPIO.output(self.pin, GPIO.LOW)

########################################################################
# Class: Motor
# Disc: Class to control the motor controllers (and associated motors)
#       on the panel. MCs require a PWM signal and two digital inputs.
#       The digital inputs control the direction of the motor:
#             EN1   EN2    EFFECT
#           - HIGH, HIGH   BRAKE
#           - HIGH, LOW    FORWARD
#           - LOW,  HIGH   REVERSE
#           - LOW,  LOW    BRAKE
#       The pwm signal controls strength of the motor in %.
#
#       NOTE: All 4 motors on this project (3x addtive, 1x outflow) only
#             flow in ONE DIRECTION. This will be considered 'forward'
#             and there will not be a way to reverse polarity
#
# Functions:
#   __init__(self, pwm, en1, en2)
#   setSpeed(self, speed)
#   brake(self)
#   runFor(self, speed, seconds)
#   abortRun(self)
#


class Motor:

    # Initialize a Relay on a Pin
    def __init__(self, en1, pwm):
        self.pwm = pwm
        self.en1 = en1
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.pwm, GPIO.OUT)
        GPIO.setup(self.en1, GPIO.OUT)
        GPIO.output(self.en1, GPIO.HIGH)
        GPIO.output(self.pwm, 0)

    # Set the speed of the motor as a decimal percent (0 - 1.0)
    # NOTE: Pi uses percent (0-100) for PWM instead of Arduino 0-255
    def setSpeed(self, speed):
        GPIO.output(self.pwm, speed)

    # Brake the motor
    def brake(self):
        GPIO.output(self.pwm, 0)

    # Runs motor at a speed for a number of seconds
    def runFor(self, speed, seconds):
        self.setSpeed(speed)
        self.t = threading.Timer(seconds, halter, {self})
        self.t.start()

    # Aborts the running of the motor and halts the timer
    def abortRun(self):
        self.t.cancel()
        self.brake()
        return

########################################################################
# Call to cleanup GPIO


def cleanupPins():
    GPIO.cleanup()

    # Custom halt


def halter(motorItem):
    motorItem.brake()
