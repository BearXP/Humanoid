#=================================================
# ** I2C Tester
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
from pca9685_driver import Device
import time

GPIO.setup("GPIO1", GPIO.OUT)
GPIO.setup("GPIO2", GPIO.IN )

def main():
    dev = Device(0x40)
    dev.set_pwm_frequency(50)   # Hz
    while True:
        for val in range(1364,2730):
            dev.set_pwm(5, val)
            time.sleep(0.01)
    


try:
	if __name__ == '__main__':
		main()
finally:
	GPIO.cleanup()
