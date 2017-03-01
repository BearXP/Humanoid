#!/usr/bin/env python
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

#DEFINE DEBUG

from pprint import pprint
import os, time
# Flash Web server
from flask import Flask, redirect, abort, url_for, render_template, \
                  request, json, g, \
                  session, \
                  flash     # flash messages
# Asynchronous webpage stuff
from flask_socketio import SocketIO, emit, join_room, leave_room, \
    close_room, rooms, disconnect
import socket
# Sqlite for poses/sequences database
import sqlite3
import sys

#------------------------------------------------
# * Setup Servos
#------------------------------------------------
NUM_SERVOS = 0
SERVOS_ACTIVE = False
#------------------------------------------------
# * Setup Servo Controller
#------------------------------------------------
try:
    #import CHIP_IO.GPIO as GPIO
    from pca9685_driver import Device
    ServoController = Device(0x40)
    print(" * Running Servos ")
    SERVOS_ACTIVE = True
    ServoController = None
except:
    print(" * Servos not connected ")
    
#------------------------------------------------
# * Setup Web Server
#------------------------------------------------
# Set this variable to "threading", "eventlet" or "gevent" to test the
# different async modes, or leave it set to None for the application to choose
# the best option based on installed packages.
async_mode = None

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, async_mode=async_mode)
#thread = None

#def background_thread():
#    """Example of how to send server generated events to clients."""
#    count = 0
#    while True:
#        socketio.sleep(10)
#        count += 1
#        socketio.emit('my_response',
#                      {'data': 'Server generated event', 'count': count},
#                      namespace='/test')

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
    rv = cur.fetchall()
    cur.close()
    return (rv[0] if rv else None) if one else rv
    
def save_db(db, sql_string):
    db.execute(sql_string)
    db.commit()

#------------------------------------------------
# *  ___       __    _   _          _      _          ___                     
# * |   \ ___ / _|  | | | |_ __  __| |__ _| |_ ___   / __| ___ _ ___ _____
# * | |) / -_)  _|  | |_| | '_ \/ _` / _` |  _/ -_)  \__ \/ -_) '_\ V / _ \
# * |___/\___|_|     \___/| .__/\__,_\__,_|\__\___|  |___/\___|_|  \_/\___/
# *                       |_|
#------------------------------------------------

def update_servo(index, pos):
    cfg = query_db('SELECT * FROM Config WHERE ID=' + str(index))[0]
    pin = cfg['Pin']
    cal_pos = 90 + cfg['Direction']*(pos-90) + cfg['Offset']
    pwm_val = int( 150.0 + float(cal_pos) * 65.0 / 18.0 )
    print("Servo:%2d, %9s-%16s Pn:%2d I2C:%s Pos:%3d>%3d>%3d" % \
        (index,
         cfg['limb'],
         cfg['name'],
         cfg['pin'],
         cfg['I2CAddr'],
         pos,
         cal_pos,
         pwm_val   ))
    if SERVOS_ACTIVE:
        ServoController = Device( int(cfg['I2CAddr'], 0) )
        ServoController.set_pwm(pin, pwm_val)
        ServoController.set_pwm_frequency(int(60))
        ServoController = None

#------------------------------------------------
# *  ___       __    _   _          _      _          ___                     
# * |   \ ___ / _|  | | | |_ __  __| |__ _| |_ ___   / __| ___ _ ___ _____ ___
# * | |) / -_)  _|  | |_| | '_ \/ _` / _` |  _/ -_)  \__ \/ -_) '_\ V / _ (_-<
# * |___/\___|_|     \___/| .__/\__,_\__,_|\__\___|  |___/\___|_|  \_/\___/__/
# *                       |_|
#------------------------------------------------

def update_servos(servos):
    print(" -> Updating servos")
    for i, pos in enumerate(servos):
        update_servo(i+1, pos)
        time.sleep(0.001)

#------------------------------------------------
# * poseDb -> servos List
#------------------------------------------------
def poseDbToList(dbRow):
    out = []
    print( dbRow )
    for i in range(NUM_SERVOS):
      out.append(dbRow['Servo%dPos' % (i+1)])
    return out


#------------------------------------------------
# * SocketIO Connect
#------------------------------------------------
@socketio.on('connect', namespace='/test')
def test_connect():
    #global thread
    #if thread is None:
    #    thread = socketio.start_background_task(target=background_thread)
    emit('my_response', {'data': 'Connected', 'count': 0})


@socketio.on('my_event', namespace='/test')
def test_message(message):
    session['receive_count'] = session.get('receive_count', 0) + 1
    emit('my_response',
         {'data': message['data'], 'count': session['receive_count']})

#------------------------------------------------
# *  ___      _                _  _                  ___               
# * / __| ___| |_ _  _ _ __   | || |___ _ __  ___   | _ \__ _ __ _ ___ 
# * \__ \/ -_)  _| || | '_ \  | __ / _ \ '  \/ -_)  |  _/ _` / _` / -_)
# * |___/\___|\__|\_,_| .__/  |_||_\___/_|_|_\___|  |_| \__,_\__, \___|
# *                   |_|                                    |___/     
#------------------------------------------------
@app.route("/",methods=['GET','POST','PUT'])
def index():
    return redirect(url_for('pose'))

#------------------------------------------------
# *  ___      _                 ___           __ _         ___               
# * / __| ___| |_ _  _ _ __    / __|___ _ _  / _(_)__ _   | _ \__ _ __ _ ___ 
# * \__ \/ -_)  _| || | '_ \  | (__/ _ \ ' \|  _| / _` |  |  _/ _` / _` / -_)
# * |___/\___|\__|\_,_| .__/   \___\___/_||_|_| |_\__, |  |_| \__,_\__, \___|
# *                   |_|                         |___/            |___/      
#------------------------------------------------
@app.route("/config")
def config():
    if request.method == 'POST':
        print("Posting")
        # Get the index of the servo being inspected
        i = str(request.form['sel-conf'][5:])
        # APPLY CONFIG
        if( 'ApplyConfig' in str(request.form) ):
            pin       = str(request.form['Servo' + i + 'Pin'])
            I2CAddr   = str(request.form['Servo' + i + 'I2CAddr'])
            offset    = str(request.form['Servo' + i + 'Offset'])
            direction = str(request.form['Servo' + i + 'Direction'])
            minimum   = str(request.form['Servo' + i + 'Minimum'])
            maximum   = str(request.form['Servo' + i + 'Maximum'])
            s = 'UPDATE Config SET' + \
                                   ' Pin='+pin+ \
                                   ", I2CAddr='"+I2CAddr+"'" \
                                   ', Offset='+offset+ \
                                   ', Direction='+direction+ \
                                   ', Minimum='+minimum+ \
                                   ', Maximum='+maximum+ \
                                   ' WHERE Id='+i+';'
            print(" -> Servo %s: SQ Executing: %s" % (i, s) )
            save_db(get_db(), s)
        # MOVE TO POS
        elif( 'MoveToPos' in str(request.form) ):
            pos = str(request.form['Servo' + i + 'Pos'])
            #print " > Updating servo %s > %s" % (i, pos)
            update_servo( int(i), int(pos) )
            #print ''
        #return redirect(url_for('config'))
        # flash("Hi world!")
    #elif request.method == 'GET':
    return render_template('Config.html',
                               configDb=query_db('select * from Config'),
                               async_mode=socketio.async_mode)

@socketio.on('move_servo', namespace='/conf')
def move_servo(message):
    position = int(message['data'])
    update_servo(1, position)

#------------------------------------------------
# *  ___      _                ___                ___               
# * / __| ___| |_ _  _ _ __   | _ \___ ___ ___   | _ \__ _ __ _ ___ 
# * \__ \/ -_)  _| || | '_ \  |  _/ _ (_-</ -_)  |  _/ _` / _` / -_)
# * |___/\___|\__|\_,_| .__/  |_| \___/__/\___|  |_| \__,_\__, \___|
# *                   |_|                                 |___/     
#------------------------------------------------
@app.route("/pose",methods=['GET','POST','PUT'])
def pose():
    if request.method == 'POST':
        # Start collecting data from input form.
        print 'POSE POSTING: %s' % request.form 
        i = str(request.form['sel-pose'])[4:]
        print 'Pose: %s' % i
        servoVals = []
        for j in range(1,19):
            servoVals.append( str(request.form[ str(i)+'.Servo'+str(j) ]) )
        # SAVEAS NEW POSE
        if( 'newName' in str(request.form) ):
            sName = str( request.form[ 'newName' ] )
            sStart = 'INSERT INTO Pose '
            sVal = "VALUES(NULL, '"+sName+"', " + ', '.join(servoVals) + ');'
            s = sStart + sVal
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
        return redirect(url_for('pose'))
    elif request.method == 'GET':
        limbs = []
        configDb = query_db('select * from Config')
        poseDb = query_db('select * from Pose order by Name Asc')
        s = 'SELECT MAX(Id) AS max_id FROM Pose;'
        maxPoseId = int(query_db(s)[0]['max_id'])
        # Generate a list of limbs
        limbs = []
        for limb in query_db("select distinct limb from Config;"):
            limbs.append( limb['limb'] )
        # Show webpage
        print " * GETTING POSE"
        return render_template('Pose.html',
                               configDb=configDb,
                               poseDb=poseDb,
                               maxPoseId=maxPoseId,
                               limbs=limbs)

#------------------------------------------------
# *  ___      _                ___                                   ___               
# * / __| ___| |_ _  _ _ __   / __| ___ __ _ _  _ ___ _ _  __ ___   | _ \__ _ __ _ ___ 
# * \__ \/ -_)  _| || | '_ \  \__ \/ -_) _` | || / -_) ' \/ _/ -_)  |  _/ _` / _` / -_)
# * |___/\___|\__|\_,_| .__/  |___/\___\__, |\_,_\___|_||_\__\___|  |_| \__,_\__, \___|
# *                   |_|                 |_|                                |___/     
#------------------------------------------------
@app.route("/sequence",methods=['GET','POST','PUT'])
def sequence():
    if request.method == 'POST':
        # Start collecting data from input form.
        i = int(str(request.form['sel-seq'])[3:])
        poseIds = []
        poseDelays = []
        for j in range(1,11):
            poseId = request.form[ "%d.%d.Pose" % (i,j) ]
            if( poseId in ['null', ''] ): poseId = -1
            poseIds.append( int(poseId) )
            poseDelay = request.form[ "%d.%d.Delay" % (i,j) ]
            if( poseDelay in ['null', ''] ): poseDelay = -1
            poseDelays.append( int(poseDelay) )
        # SAVEAS NEW SEEQUENCE
        if( 'newName' in str(request.form) ):
            sName = str( request.form[ 'newName' ] )
            s = poseIds + poseDelays
            s[::2] = poseIds
            s[1::2] = poseDelays
            s = s + [0] * (64-len(s))
            s = ["%d" % i for i in s]
            s = ", ".join(s)
            s = "INSERT INTO Sequence VALUES(NULL, '"+sName+"', " + s + ");"
            print("Running SQL String: %s" % s )
            save_db(get_db(), s)
        # DELETE SEQUENCE
        elif( 'delName' in str(request.form) ):
            s = 'DELETE FROM Sequence WHERE ID='+str(i)
            print("Running SQL String: %s" % s )
            save_db(get_db(), s)
        # SAVE SEQUENCE
        elif( request.form['submit'] == 'Save Sequence' ):
            s1 = ['Pose%d=%d' % (k+1, x) for k,x in enumerate(poseIds)]
            s2 = ['Delay%dms=%d' % (k+1, x) for k,x in enumerate(poseDelays)]
            s = ', '.join(s1 + s2)
            s = 'UPDATE Sequence SET ' + s + ' WHERE Id='+str(i)+';'
            print("Running SQL String: %s" % s )
            save_db(get_db(), s)
        # EXECUTE SEQUENCE
        elif( request.form['submit'] == 'Execute Sequence' ):
            for i in range(len(poseIds)):
                if( poseIds[i] != -1 and poseDelays[i] != -1 ):
                    pose = query_db('select * from Pose where Id=%d' % poseIds[i])[0]
                    update_servos(poseDbToList(pose))
                    time.sleep(poseDelays[i]/1000.0)
            return
        return redirect(url_for('sequence'))
    elif request.method == 'GET':
        poseDb = query_db('select * from Pose order by Name Asc')
        seqDb = query_db('select * from Sequence order by Name Asc')
        s = 'SELECT MAX(Id) AS max_id FROM Sequence;'
        maxSeqId = int(query_db(s)[0]['max_id'])
        return render_template('Sequence.html',
                               poseDb=poseDb,
                               maxSeqId=maxSeqId,
                               seqDb=seqDb)


#------------------------------------------------
# *  __  __      _         ___                       _           
# * |  \/  |__ _(_)_ _    | _ \_ _ ___  __ ___ _____(_)_ _  __ _ 
# * | |\/| / _` | | ' \   |  _/ '_/ _ \/ _/ -_|_-<_-< | ' \/ _` |
# * |_|  |_\__,_|_|_||_|  |_| |_| \___/\__\___/__/__/_|_||_\__, |
# *                                                        |___/ 
#------------------------------------------------
if __name__ == "__main__":
    try:
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
        socketio.run(app,
                     #host=str(s),
                     debug=True,
                     port=5000,
                     use_reloader=True)
    finally:
        #GPIO.cleanup()
        #disconnect()
        #thread.stop_background_task()
        1+1
