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

from pprint import pprint
import os, time
# Flash Web server
from flask import Flask, redirect, abort, url_for, render_template, \
                  request, json, g, \
                  flash     # flash messages
import socket
# Sqlite for poses/sequences database
#from sqlite3 import dbapi2 as sqlite3
import sqlite3
import sys

#import CHIP_IO.GPIO as GPIO
#from pca9685_driver import Device

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
# * Setup Servos
#------------------------------------------------
NUM_SERVOS = 0
SERVOS_ACTIVE = False
#------------------------------------------------
# * Setup Servo Controller
#------------------------------------------------
try:
    ServoController = Device(0x40)
    print(" * Running Servos ")
    SERVOS_ACTIVE = True
    ServoController = None
except:
    print(" * Servos not connected ")

#------------------------------------------------
# * Update Servos function
#------------------------------------------------
def update_servos(servos):
    if SERVOS_ACTIVE:
        for i, pos in enumerate(servos):
            cfg = query_db('SELECT * FROM Config WHERE ID=' + str(i+1))[0]
            pin = cfg['Pin']
            ServoController = Device( cfg['I2CAddr'] )
            ServoController.set_pwm_frequency(60)
            pwm_val = int( 150.0 + float(pos) * 65.0 / 18.0 )
            print("Servo"+str(i)+" > "+str(pwm_val))
            ServoController.set_pwm(pin, pwm_val)
            time.sleep(0.01)

#------------------------------------------------
# * Setup Web Page
#------------------------------------------------
@app.route("/",methods=['GET','POST','PUT'])
def index():
    return redirect(url_for('pose'))

#------------------------------------------------
# * Setup Config Page
#------------------------------------------------
@app.route("/config",methods=['GET','POST','PUT'])
def config():
    if request.method == 'POST':
        i = str(request.form['sel-conf'][5:])
        pin = str(request.form['Servo' + i + 'Pin'])
        I2CAddr = str(request.form['Servo' + i + 'I2CAddr'])
        print( "I2C: " + str(I2CAddr) )
        offset = str(request.form['Servo' + i + 'Offset'])
        direction = str(request.form['Servo' + i + 'Direction'])
        minimum = str(request.form['Servo' + i + 'Minimum'])
        maximum = str(request.form['Servo' + i + 'Maximum'])
        s = 'UPDATE Config SET' + \
                               ' Pin='+pin+ \
                               ", I2CAddr='"+I2CAddr+"'" \
                               ', Offset='+offset+ \
                               ', Direction='+direction+ \
                               ', Minimum='+minimum+ \
                               ', Maximum='+maximum+ \
                               ' WHERE Id='+i+';'
        save_db(get_db(), s)
        # flash("Hi world!")
    return render_template('Config.html',
                           configDb=query_db('select * from Config'))


#------------------------------------------------
# * Setup POSE Page
#------------------------------------------------
@app.route("/pose",methods=['GET','POST','PUT'])
def pose():
    if request.method == 'POST':
        # Start collecting data from input form.
        i = str(request.form['sel-pose'])[4:]
        servoVals = []
        for j in range(1,19):
            servoVals.append( str(request.form[ str(i)+'.Servo'+str(j) ]) )
        # SAVEAS NEW POSE
        if( 'newName' in str(request.form) ):
            sName = str( request.form[ 'newName' ] )
            sStart = 'INSERT INTO Pose '
            sIns = '(Name, '
            sIns += ', '.join(['Servo%dPos' % (k+1) for k in range(NUM_SERVOS)])
            sIns += ') '
            sVal = "VALUES(NULL, '"+sName+"', " + ', '.join(servoVals) + ');'
            s = sStart + sVal
            print(s)
            save_db(get_db(), s)
        # DELETE POSE
        elif( 'delName' in str(request.form) ):
            s = 'DELETE FROM Pose WHERE ID='+str(i)
            save_db(get_db(), s)
        # EXECUTE POSE
        elif( request.form['submit'] == 'Move to Pose' ):
            vals = ( [int(i) for i in servoVals] )
            update_servos(vals)
        # SAVE POSE
        elif( request.form['submit'] == 'Save Pose' ):
            s = ['Servo%dPos=%s' % (k+1, x) for k,x in enumerate(servoVals)]
            s = ', '.join(s)
            s = 'UPDATE Pose SET ' + s + ' WHERE Id='+i+';'
            save_db(get_db(), s)
    elif request.method == 'GET':
        limbs = []
        configDb = query_db('select * from Config')
        poseDb = query_db('select * from Pose order by Name Asc')
        # Generate a list of limbs
        limbs = []
        for limb in query_db("select distinct limb from Config;"):
        	limbs.append( limb['limb'] )
        # Show webpage
        return render_template('Pose.html',
                               configDb=configDb,
                               poseDb=poseDb,
                               limbs=limbs)
    return 'OK'

#------------------------------------------------
# * Setup SEQUENCE Page
#------------------------------------------------
@app.route("/sequence",methods=['GET','POST','PUT'])
def seq():
    if request.method == 'POST':
        i = str(request.form['sel-seq'])[3:]
        print("Updating sequence #%d" % i)
        poseIds = []
        poseDelays = []
        for j in range(1,11):
            poseIds.append( int(request.form[ "%d.%d.Pose" % (i,j) ]) )
            poseDelays.append( int(request.form[ "%d.%d.Delay" % (i,j) ]) )
        # SAVE SEQUENCE
        if( request.form['submit'] == 'Save Sequence' ):
            s1 = ['Pose%d=%d' % (k+1, x) for k,x in enumerate(poseIds)]
            s2 = ['Delay%dms=%d' % (k+1, x) for k,x in enumerate(poseDelays)]
            s = ', '.join(s1 + s2)
            s = 'UPDATE Sequence SET ' + s + ' WHERE Id='+i+';'
            save_db(get_db(), s)
    elif request.method == 'GET':
        poseDb = query_db('select * from Pose order by Name Asc')
        seqDb = query_db('select * from Sequence order by Name Asc')
        return render_template('Sequence.html',
                               poseDb=poseDb,
                               seqDb=seqDb)

#------------------------------------------------
# * MAIN Processing
#------------------------------------------------
if __name__ == "__main__":
    #try:
    #  Get the NUM_SERVOS
    with app.app_context():
        s = 'SELECT MAX(Id) AS max_id FROM Config;'
        NUM_SERVOS = int(query_db(s)[0]['max_id'])
    # Report the local IP address so external PC's can find me and connect
    s = [(s.connect(('8.8.8.8', 53)),
          s.getsockname()[0],
          s.close()) for s in [socket.socket(socket.AF_INET,
                                             socket.SOCK_DGRAM)]][0][1]
    print(' * ' + s)
    # Run the web server
    app.run(host=str(s),
            debug=1,
            port=5000,
            use_reloader=True)
    #finally:
        #GPIO.cleanup()
