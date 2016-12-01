from pca9685_driver import Device
import time

# 0x40 from i2cdetect -y 1 (1 if Raspberry pi 2)
dev = Device(0x40)

# set the pwm frequency (Hz)
dev.set_pwm_frequency(1000)

# set the duty cycle for LED05 to 50%
dev.set_pwm(5, 2047)

for i in range(1000,4000):
    dev.set_pwm(5,i)
    time.sleep(0.01)
