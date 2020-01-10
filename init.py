#! /usr/bin/python3

import time
import sys
import requests

current_beverage = sys.argv[1]

COLD_BREW = 'coldBrew'
KOMBUCHA = 'kombucha'
AVAILABLE_DRINKS = (COLD_BREW, KOMBUCHA)

if current_beverage not in AVAILABLE_DRINKS:
    raise Exception("First argument must be the beverage you are measuring\n{}".format(AVAILABLE_DRINKS))

EMULATE_HX711 = False

# TODO find out what the reference unit is here
reference_unit = 1

# TODO determine what values need to be put here after calibrating the scale
weight_value_map = {
    [COLD_BREW]: {
        0: 900,    # we are out
        1: 12500,  # almost out
        2: 24000,  # going quickly!
        3: 36000,  # we have some!
    },
    [KOMBUCHA]: {
        0: 900,    # we are out
        1: 12500,  # almost out
        2: 24000,  # going quickly!
        3: 36000,  # we have some!
    }
}

weight_values = weight_value_map[current_beverage]

if not EMULATE_HX711:
    import RPi.GPIO as GPIO
    from hx711 import HX711
else:
    from emulated_hx711 import HX711


def clean_and_exit():
    print("Cleaning...")

    if not EMULATE_HX711:
        GPIO.cleanup()

    print("Bye!")
    sys.exit()


hx = HX711(5, 6)

# I've found out that, for some reason, the order of the bytes is not always the same
# between versions of python, numpy and the hx711 itself.
# Still need to figure out why does it change.
# If you're experiencing super random values, change these values to MSB or LSB until to get more stable values.
# There is some code below to debug and log the order of the bits and the bytes.
# The first parameter is the order in which the bytes are used to build the "long" value.
# The second paramter is the order of the bits inside each byte.
# According to the HX711 Datasheet, the second parameter is MSB so you shouldn't need to modify it.
hx.set_reading_format("MSB", "MSB")

# HOW TO CALCULATE THE REFFERENCE UNIT
# To set the reference unit to 1. Put 1kg on your sensor or anything you have and know exactly how much it weights.
# In this case, 92 is 1 gram because, with 1 as a reference unit I got numbers near 0 without any weight
# and I got numbers around 184000 when I added 2kg. So, according to the rule of thirds:
# If 2000 grams is 184000 then 1000 grams is 184000 / 2000 = 92.
# hx.set_reference_unit(113)
hx.set_reference_unit(reference_unit)

hx.reset()

hx.tare()

print("Tare done! Add weight now...")

# to use both channels, you'll need to tare them both
# hx.tare_A()
# hx.tare_B()

while True:
    try:
        # These three lines are useful to debug whether to use MSB or LSB in the reading formats
        # for the first parameter of "hx.set_reading_format("LSB", "MSB")".
        # Comment the two lines "val = hx.get_weight(5)" and "print val" and uncomment
        # these three lines to see what it prints.

        # np_arr8_string = hx.get_np_arr8_string()
        # binary_string = hx.get_binary_string()
        # print binary_string + " " + np_arr8_string

        # Prints the weight. Comment if you're debugging the MSB and LSB issue.
        current_weight = hx.get_weight(5)

        send_level = 0

        # determine the response value we should send
        for i in weight_values:
            check_weight = weight_values[i]

            if current_weight < check_weight:
                send_level = i
                break
            else:
                send_level = i+1

        # To get weight from both channels (if you have load cells hooked up
        # to both channel A and B), do something like this
        # val_A = hx.get_weight_A(5)
        # val_B = hx.get_weight_B(5)
        # print "A: %s  B: %s" % ( val_A, val_B )

        hx.power_down()

        body = {
            [current_beverage]: send_level
        }

        requests.post('http://whats-on-tap.nextwebtoday.com/api', data=body)

        hx.power_up()
        time.sleep(1)

    except (KeyboardInterrupt, SystemExit):
        clean_and_exit()
