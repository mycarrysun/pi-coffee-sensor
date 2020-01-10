#! /usr/bin/python3

import time
import sys
import requests

sleep_time = 1

COLD_BREW = 'coldBrew'
KOMBUCHA = 'kombucha'


def get_switch_value(switch):
    # TODO get the switches value here
    value = 0
    return value


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
