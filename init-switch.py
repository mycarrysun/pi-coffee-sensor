#! /usr/bin/python3

import time
import requests
import RPi.GPIO as GPIO

sleep_time = 1

COLD_BREW = 'coldBrew'
KOMBUCHA = 'kombucha'
PIN_LAYOUT = {
    [COLD_BREW]: 1,
    [KOMBUCHA]: 2,
}


def get_switch_value(switch):
    GPIO.setmode(GPIO.BOARD)
    pin = PIN_LAYOUT[switch]
    GPIO.setup(pin, GPIO.IN)

    return GPIO.input(pin)


while True:
    try:

        body = {
            [COLD_BREW]: get_switch_value(COLD_BREW),
            [KOMBUCHA]: get_switch_value(KOMBUCHA),
        }

        requests.post('http://whats-on-tap.nextwebtoday.com/api', data=body)

        time.sleep(sleep_time)

    except (KeyboardInterrupt, SystemExit):
        exit()
