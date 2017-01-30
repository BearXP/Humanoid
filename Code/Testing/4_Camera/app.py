#!/usr/bin/env python
from flask import Flask, render_template, Response
import os

app = Flask(__name__)

@app.route('/')
def index():
    """Video streaming home page."""
    return render_template('index.html')


def gen(camera_id):
    """Video streaming generator function."""
    while True:
        os.system("uvccapture -v -m -d/dev/video"+str(camera_id)+" -ovideo"+str(camera_id)+".jpg")
        frame = open('Pic.jpg', 'rb').read()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')


@app.route('/video_feed')
def video_feed(index=0):
    """Video streaming route. Put this in the src attribute of an img tag."""
    return Response(gen(index),
                    mimetype='multipart/x-mixed-replace; boundary=frame')


if __name__ == '__main__':
    app.run(host='192.168.49.101', debug=True, threaded=True)
