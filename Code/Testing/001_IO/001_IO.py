#=================================================
# ** IO Tester
#------------------------------------------------
# Date created: 23/Nov/2016
# Created by:   Night_Runner
# Description:
#  Cycles GPIO1 (XIO-2) low and high, while
#  reporting the state of GPIO2 (XIO-3).
#  GPIO1 & GPIO2 should be shorted to test
#  that IO is working correctly.
# Libraries:
#  github.com/xtacocorex/CHIP_IO.git
#=================================================

import CHIP_IO.GPIO as GPIO
import time

GPIO.setup("GPIO1", GPIO.OUT)
GPIO.setup("GPIO2", GPIO.IN )

def main():
	out_state = 0
	while True:
		# Toggle the output state
		out_state = 1 - out_state
		# Write the output state to the pin
		if out_state:
			GPIO.output("GPIO1", GPIO.HIGH)
			print("Writing HIGH to output pin")
		else:
			GPIO.output("GPIO1", GPIO.LOW )
			print("Writing LOW to output pin")
		
		# Read the input
		if GPIO.input("GPIO2"):
			print("Reading HIGH")
		else:
			print("Reading LOW" )
		
		# Sleep for 2 seconds
		time.sleep(2)


try:
	if __name__ == '__main__':
		main()
finally:
	GPIO.cleanup()
