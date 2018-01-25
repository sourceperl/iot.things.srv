#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import datetime
from functools import wraps
from flask import Flask, make_response, request, render_template, jsonify, Response
from pymongo import MongoClient
import pytz

# some const
LOCAL_TZ = pytz.timezone('Europe/Paris')

# init mongo
db = MongoClient().iot


# some class
class localFlask(Flask):
    # force anonymous server name
    def process_response(self, response):
        response.headers['server'] = 'HTTP client server'
        super(localFlask, self).process_response(response)
        return(response)


# some functions
def check_auth(username, password):
    """This function is called to check if a username /
    password combination is valid.
    """
    return username == 'admin' and password == 'secret'

def authenticate():
    """Sends a 401 response that enables basic auth"""
    return Response(
    'Could not verify your access level for that URL.\n'
    'You have to login with proper credentials', 401,
    {'WWW-Authenticate': 'Basic realm="Login Required"'})

def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        if not auth or not check_auth(auth.username, auth.password):
            return authenticate()
        return f(*args, **kwargs)
    return decorated

def datetimefilter(dt, fmt='%Y-%m-%d %H:%M:%S'):
    utc_dt = pytz.utc.localize(dt)
    return utc_dt.astimezone(LOCAL_TZ).strftime(fmt)




# Flask app
app = localFlask(__name__)
app.jinja_env.filters['datetimefilter'] = datetimefilter


@app.route('/')
@app.route('/dashboard/<string:board>')
@requires_auth
def dashboard(board='list'):
    if board == 'list':
        l_dev = db.tx_pulse_devices.find()
        return render_template('dashboard.html', board='list', devices=l_dev)
    else:
        return render_template('dashboard.html', board=board)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)
