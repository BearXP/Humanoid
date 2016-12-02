#=================================================
# ** Main
#------------------------------------------------
# Date created: 2/Dec/2016
# Created by:   Mark Evans
# Description:
#  Cycles GPIO1 (XIO-2) low and high, while
#  reporting the state of GPIO2 (XIO-3).
#  GPIO1 & GPIO2 should be shorted to test
#  that IO is working correctly.
# Libraries:
#  github.com/xtacocorex/CHIP_IO.git
#  http://flask.pocoo.org/docs/0.11/
#=================================================

from flask import Flask, redirect, abort, url_for, render_template, request
import CHIP_IO.GPIO as GPIO
from pca9685_driver import Device
import time

NUM_SERVOS = 16

servoDb = [ {'index':index,'limb':'','name':'','pos':90,'min':0,'max':180} for index in range(NUM_SERVOS+1) ]
servoDb[ 1]['limb'] = 'Neck'
servoDb[ 1]['name'] = 'Spin'
servoDb[ 2]['limb'] = 'Neck'
servoDb[ 2]['name'] = 'Nod'
servoDb[ 3]['limb'] = 'LArm'
servoDb[ 3]['name'] = 'Shoulder rotate'
servoDb[ 4]['limb'] = 'LArm'
servoDb[ 4]['name'] = 'Shoulder up/down'
servoDb[ 5]['limb'] = 'LArm'
servoDb[ 5]['name'] = 'Elbow'
servoDb[ 6]['limb'] = 'LArm'
servoDb[ 6]['name'] = 'Grip'
servoDb[ 7]['limb'] = 'RArm'
servoDb[ 7]['name'] = 'Shoulder rotate'
servoDb[ 8]['limb'] = 'RArm'
servoDb[ 8]['name'] = 'Shoulder up/down'
servoDb[ 9]['limb'] = 'RArm'
servoDb[ 9]['name'] = 'Elbow'
servoDb[10]['limb'] = 'RArm'
servoDb[10]['name'] = 'Grip'

servoDb[11]['limb'] = 'LLeg'
servoDb[11]['name'] = 'Hip'
servoDb[12]['limb'] = 'LLeg'
servoDb[12]['name'] = 'Knee'
servoDb[13]['limb'] = 'LLeg'
servoDb[13]['name'] = 'Ankle'

servoDb[14]['limb'] = 'RLeg'
servoDb[14]['name'] = 'Hip'
servoDb[15]['limb'] = 'RLeg'
servoDb[15]['name'] = 'Knee'
servoDb[16]['limb'] = 'RLeg'
servoDb[16]['name'] = 'Ankle'

limbs = []
for i in range(1,NUM_SERVOS+1):
    if not servoDb[i]['limb'] in limbs:
        if not servoDb[i]['limb'] == '':
            limbs.append(servoDb[i]['limb'])

ServoController = Device(0x40)
ServoController.set_pwm_frequency(60)

app = Flask(__name__)

def update_servos():
    for i in range (1,NUM_SERVOS+1):
        servoDb[i]['pos'] = request.form['Servo' + str(i)]
        pwm_val = 150 + servoDb[i]['pos'] * 65.0 / 18.0
        ServoController.set_pwm(i, int(pwm_val))


@app.route("/",methods=['GET','POST','PUT'])
def index():
    if request.method == 'POST':
        update_servos()
    return render_template('hello.html', limbs=limbs, servoDb=servoDb)


if __name__ == "__main__":
    try:
        app.run(host="0.0.0.0", debug=1)
    finally:
        GPIO.cleanup()
