#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import datetime
import os
from functools import wraps
from flask import Flask, make_response, redirect, request, render_template, url_for, Response, g
from pymongo import MongoClient
import pandas as pd
import numpy as np
import pytz

# some const
LOCAL_TZ = pytz.timezone('Europe/Paris')

# init mongo
db = MongoClient().iot


# some class
class localFlask(Flask):
    # force anonymous server name
    def process_response(self, response):
        response.headers['server'] = 'ThingView server'
        super(localFlask, self).process_response(response)
        return(response)


# some functions
def get_user_lvl(username, password):
    # get user access level (0: no auth, 1-3:valid)
    u_info = db.users.find_one({'$query': {'user': username, 'pwd': password}})
    if u_info:
        return u_info['level']
    else:
        return 0

def authenticate():
    return Response('You have to login with proper credentials', 401, {'WWW-Authenticate': 'Basic realm="Login Required"'})

def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        # check auth (if exist)
        auth = request.authorization
        if auth:
            g.user_lvl = get_user_lvl(auth.username, auth.password)
        else:
            g.user_lvl = 0
        # check user level (0: no auth, 1-3:valid)
        if g.user_lvl in [1,2,3] :
            g.is_admin = g.user_lvl == 3
            return f(*args, **kwargs)
        else:
            return authenticate()
    return decorated

def datetimefilter(dt, fmt='%Y-%m-%d %H:%M:%S'):
    utc_dt = pytz.utc.localize(dt)
    return utc_dt.astimezone(LOCAL_TZ).strftime(fmt)


# Flask app
app = localFlask(__name__)
app.jinja_env.filters['datetimefilter'] = datetimefilter


@app.route('/')
@requires_auth
def root():
    return redirect(url_for('devices'))

@app.route('/logout')
def logout():
    return Response('things to do here')

@app.route('/devices')
@requires_auth
def devices():
    l_dev = db.devices.find()
    return render_template('devices.html', devices=l_dev)

@app.route('/things/tx_pulse/<string:device_id>')
@requires_auth
def thing_tx_pulse(device_id):
    # device data
    device = db.devices.find_one({'$query': {'device_id': device_id}})
    # convert raw data (raw to daily data)
    df_raw = pd.DataFrame(None, columns=['vm', 'vc'], dtype='float')
    for record in db.tx_pulse_raw.find({'$query': {'device_id': device_id}, '$orderby': {'msg_time': -1}}).limit(400):
        df_raw.loc[record['msg_time'].replace(tzinfo=pytz.utc).astimezone(LOCAL_TZ)] = [record['pulse_1'], record['pulse_2']]
    # add weight for vc
    df_raw['vc'] *= 10
    # resample:
    # - for 5h gas time: use the max rx index value for 5h00 to 5h59 time window
    df_h = df_raw.resample('H', closed='left', label='left', how=np.max).interpolate().diff()
    df_j = df_h.resample(rule='24H', closed='left', label='left', base=6, how=np.sum)
    # web render
    return render_template('things/tx_pulse.html', device=device, 
                           df_raw=df_raw[:3], df_h=df_h.sort(ascending=False)[:24], df_j=df_j.sort(ascending=False)[:7])


if __name__ == '__main__':
    # auto-reload when templates dir is update
    extra_dirs = ['templates',]
    extra_files = extra_dirs[:]
    for extra_dir in extra_dirs:
        for dirname, dirs, files in os.walk(extra_dir):
            for filename in files:
                filename = os.path.join(dirname, filename)
                if os.path.isfile(filename):
                    extra_files.append(filename)
    # define SSL
    ssl_ctx = ('ssl.cert', 'ssl.key')
    # start flask with auto-reload
    app.run(host='0.0.0.0', port=8080, ssl_context=ssl_ctx, extra_files=extra_files, debug=True)
