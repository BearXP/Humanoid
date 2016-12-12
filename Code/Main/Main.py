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

import os
from flask import Flask, redirect, abort, url_for, render_template, request
import sqlite3
import socket
#import CHIP_IO.GPIO as GPIO
from pca9685_driver import Device
import time

NUM_SERVOS = 16

servoDb = [ {'index':index,'limb':'','name':'','pos':90,'min':0,'max':180} for index in range(NUM_SERVOS+1) ]
servoDb[ 0]['limb'] = 'Neck'
servoDb[ 0]['name'] = 'Spin'
servoDb[ 1]['limb'] = 'Neck'
servoDb[ 1]['name'] = 'Nod'
servoDb[ 2]['limb'] = 'LArm'
servoDb[ 2]['name'] = 'Shoulder rotate'
servoDb[ 3]['limb'] = 'LArm'
servoDb[ 3]['name'] = 'Shoulder up/down'
servoDb[ 4]['limb'] = 'LArm'
servoDb[ 4]['name'] = 'Elbow'
servoDb[ 5]['limb'] = 'LArm'
servoDb[ 5]['name'] = 'Grip'
servoDb[ 6]['limb'] = 'RArm'
servoDb[ 6]['name'] = 'Shoulder rotate'
servoDb[ 7]['limb'] = 'RArm'
servoDb[ 7]['name'] = 'Shoulder up/down'
servoDb[ 8]['limb'] = 'RArm'
servoDb[ 8]['name'] = 'Elbow'
servoDb[ 9]['limb'] = 'RArm'
servoDb[ 9]['name'] = 'Grip'
servoDb[10]['limb'] = 'LLeg'
servoDb[10]['name'] = 'Hip'
servoDb[11]['limb'] = 'LLeg'
servoDb[11]['name'] = 'Knee'
servoDb[12]['limb'] = 'LLeg'
servoDb[12]['name'] = 'Ankle'
servoDb[13]['limb'] = 'RLeg'
servoDb[13]['name'] = 'Hip'
servoDb[14]['limb'] = 'RLeg'
servoDb[14]['name'] = 'Knee'
servoDb[15]['limb'] = 'RLeg'
servoDb[15]['name'] = 'Ankle'

limbs = []
for i in range(NUM_SERVOS):
    if not servoDb[i]['limb'] in limbs:
        if not servoDb[i]['limb'] == '':
            limbs.append(servoDb[i]['limb'])

ServoController = Device(0x40)
ServoController.set_pwm_frequency(60)

app = Flask(__name__)
# create config variable, which acts like a dicto
app.config.from_object(__name__)

# Load the default config and oberride config from environment variable
app.config.update(dict(
  DATABASE=os.path.join(app.root_path, 'patterns.db'),
  SECRET_KEY='123',
  USERNAME='admin',
  PASSWORD='admin'
))
app.config.from_envvar('FLASKR_SETTINGS', silent=True)

def update_servos():
    for i in range (NUM_SERVOS):
        servoDb[i]['pos'] = request.form['Servo' + str(i)]
        pwm_val = int( 150.0 + float(servoDb[i]['pos']) * 65.0 / 18.0 )
        print("Servo"+str(i)+": "+str(servoDb[i]['pos'])+" > "+str(pwm_val))
        ServoController.set_pwm(i, int(pwm_val))
        time.sleep(0.01)


@app.route("/",methods=['GET','POST','PUT'])
def index():
    if request.method == 'POST':
        update_servos()
    return render_template('hello.html', limbs=limbs, servoDb=servoDb)


if __name__ == "__main__":
    #try:
    print([(s.connect(('8.8.8.8', 53)), s.getsockname()[0], s.close()) for s in [socket.socket(socket.AF_INET, socket.SOCK_DGRAM)]][0][1])
    app.run(host="0.0.0.0", debug=1)
    #finally:
        #GPIO.cleanup()
