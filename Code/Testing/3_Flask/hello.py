# http://flask.pocoo.org/docs/0.11/

from flask import Flask, redirect, abort, url_for, render_template, request
from collections import namedtuple

NUM_SERVOS = 16

servoDb = [ {'index':index,'limb':'','name':'','pos':90,'max':180} for index in range(NUM_SERVOS) ]
servoDb[ 1]['limb'] = 'Neck'
servoDb[ 1]['name'] = 'Spin'
servoDb[ 2]['limb'] = 'Neck'
servoDb[ 2]['name'] = 'Nod'
servoDb[ 3]['limb'] = 'Larm'
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

limbs = []
for i in range(NUM_SERVOS):
    if not servoDb[i]['limb'] in limbs:
        limbs.append(servoDb[i]['limb'])


app = Flask(__name__)

def update_servos():
    if(request.form['Servo'] == 'Neck'):
        pwm_servo(1, request.form['Servo1'])
        pwm_servo(2, request.form['Servo2'])


@app.route("/",methods=['GET','POST','PUT'])
def index():
    if request.method == 'POST':
        update_servos()
    return render_template('hello.html', limbs=limbs, servoDb=servoDb)


if __name__ == "__main__":
    app.run(host="0.0.0.0")
