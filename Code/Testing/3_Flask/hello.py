# http://flask.pocoo.org/docs/0.11/

from flask import Flask, redirect, abort, url_for, render_template, request
app = Flask(__name__)


def update_servos():
    if(request.form['Servo'] == 'Neck'):
        pwm_servo(1, request.form['Servo1'])
        pwm_servo(2, request.form['Servo2'])


@app.route("/",methods=['GET','POST','PUT'])
def index():
    if request.method == 'POST':
        update_servos()
    return render_template('hello.html')


if __name__ == "__main__":
    app.run(host="0.0.0.0")
