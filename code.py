# Advent of Code "Trophy"

# IMPORTS --------------------------------------------------------------------
import board
import digitalio
import time

# SETUP ----------------------------------------------------------------------

led = digitalio.DigitalInOut(board.LED)
led.direction = digitalio.Direction.OUTPUT

print("Init complete.")


# LOOP -----------------------------------------------------------------------

print("Starting loop...")

while True:
    led.value = True
    time.sleep(0.5)
    led.value = False
    time.sleep(0.5)

    print("bottom of loop...")
