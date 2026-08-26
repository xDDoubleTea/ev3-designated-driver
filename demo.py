#!/usr/bin/env python3

import random
from time import sleep
from ev3dev2.motor import OUTPUT_A, OUTPUT_B, SpeedPercent, MoveTank
from ev3dev2.sensor import INPUT_1
from ev3dev2.sensor.lego import UltrasonicSensor

tank = MoveTank(OUTPUT_A, OUTPUT_B)
us = UltrasonicSensor(INPUT_1)


TURN_SPEED = SpeedPercent(-15)
TURN_SPEED_REV = SpeedPercent(15)

WHEEL_DIAMETER_MM = 81.6
# Effective, not measured. The ruler says the axle track is ~155 mm, but the
# wide tires scrub and pivot inboard of the tread centre, so the robot turns as
# if the track were smaller. This value is calibrated against the mat rather
# than the ruler -- re-tune it here if the robot over- or under-shoots a real
# 90 degrees, and every derived angle follows.
AXLE_TRACK_MM = 150.53


def turn_degrees(robot_degrees):
    """Motor degrees needed to spin the robot in place by robot_degrees.

    Each wheel traces an arc of (track / 2) * angle, and the wheel travels
    (pi * diameter) per motor revolution, so the diameter cancels down to:
        motor_degrees = robot_degrees * track / diameter
    """
    return robot_degrees * AXLE_TRACK_MM / WHEEL_DIAMETER_MM


TURN_DEGREES = turn_degrees(90)


def forward():
    tank.on(TURN_SPEED, TURN_SPEED)


def back(seconds=0.3):
    tank.on_for_seconds(TURN_SPEED_REV, TURN_SPEED_REV, seconds)


def turn_left(degrees=TURN_DEGREES):
    tank.on_for_degrees(TURN_SPEED_REV, TURN_SPEED, degrees)


def turn_right(degrees=TURN_DEGREES):
    tank.on_for_degrees(TURN_SPEED, TURN_SPEED_REV, degrees)


try:
    while True:
        distance = us.distance_centimeters
        # print(distance)
        if distance < 25:
            tank.stop()
            sleep(2)
            back(seconds=1)
            decide = random.randint(1, 2)
            tank.stop()
            sleep(1)
            if decide == 1:
                turn_left()
            elif decide == 2:
                turn_right()
        else:
            forward()

        sleep(0.05)
except KeyboardInterrupt:
    tank.stop()
