#!/usr/bin/env python3

from time import sleep
import ev3dev2.fonts as fonts
from ev3dev2.motor import LargeMotor, OUTPUT_A, OUTPUT_B, SpeedPercent, MoveTank
from ev3dev2.sensor import INPUT_1
from ev3dev2.sensor.lego import TouchSensor, UltrasonicSensor
from ev3dev2.led import Leds

from ev3dev2.display import Display


while True:
    us = UltrasonicSensor(INPUT_1)

    display = Display()
    distance = us.distance_centimeters
    distance_str = "Distance {:.1f} cm".format(distance)
    display.draw.text((10, 10), distance_str, font=fonts.load("luBS18"))
    display.update()
    sleep(0.05)
