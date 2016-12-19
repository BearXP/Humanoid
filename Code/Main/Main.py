#=================================================
# ** Main
#------------------------------------------------
# Date created: 17/Dec/2016
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

import os, time
# Flash Web server
from flask import Flask, redirect, abort, url_for, render_template, request, g
import socket
# Sqlite for poses/sequences database
#from sqlite3 import dbapi2 as sqlite3
import sqlite3
import sys

#import CHIP_IO.GPIO as GPIO
#from pca9685_driver import Device

#------------------------------------------------
# * Setup Servos
#------------------------------------------------

#------------------------------------------------
# * Setup Servo Controller
#------------------------------------------------
#ServoController = Device(0x40)
#ServoController.set_pwm_frequency(60)

#------------------------------------------------
# * Setup Web Server
#------------------------------------------------
app = Flask(__name__)
# create config variable, which acts like a dicto
app.config.from_object(__name__)

#------------------------------------------------
# * Setup SQL database
#------------------------------------------------
DATABASE = 'Robobot.db'

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        db.row_factory = sqlite3.Row
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

def query_db(query, args=(), one=False):
    cur = get_db().execute(query, args)
    #cur = get_db().cursor();
    #cur.execute(query, args)
    rv = cur.fetchall()
    cur.close()
    return (rv[0] if rv else None) if one else rv
    
def save_db(db, sql_string):
    db.execute(sql_string)
    db.commit()


#------------------------------------------------
# * Update Servos function
#------------------------------------------------
def update_servos():
    for i in range (NUM_SERVOS):
        servoDb[i]['pos'] = request.form['Servo' + str(i)]
        pwm_val = int( 150.0 + float(servoDb[i]['pos']) * 65.0 / 18.0 )
        print("Servo"+str(i)+": "+str(servoDb[i]['pos'])+" > "+str(pwm_val))
        #ServoController.set_pwm(i, int(pwm_val))
        time.sleep(0.01)

#------------------------------------------------
# * Setup Web Page
#------------------------------------------------
@app.route("/",methods=['GET','POST','PUT'])
def index():
    if request.method == 'POST':
        update_servos()
    for servo in query_db('select * from Config'):
      print str(servo["limb"])
    return render_template('Config.html', configDb=query_db('select * from Config'))
    
#------------------------------------------------
# * Setup Web Page
#------------------------------------------------
@app.route("/config",methods=['GET','POST','PUT'])
def config():
    if request.method == 'POST':
        for i in range(1..19):
            offset = request.form['Servo' + str(i) + 'Offset']
            minimum = request.form['Servo' + str(i) + 'Min']
            maximum = request.form['Servo' + str(i) + 'Max']
            query_db('UPDATE Config SET offset='+offset+', min='+minimum+', max='+maximum+' WHERE Id='+i+';')
            
    return render_template('Config.html', configDb=query_db('select * from Config'))


#------------------------------------------------
# * Main Processing
#------------------------------------------------
if __name__ == "__main__":
    #try:
    print([(s.connect(('8.8.8.8', 53)), s.getsockname()[0], s.close()) for s in [socket.socket(socket.AF_INET, socket.SOCK_DGRAM)]][0][1])
    app.run(host="0.0.0.0", debug=1)
    #finally:
        #GPIO.cleanup()
