from functools import wraps
from flask import redirect, render_template, session, url_for, g, jsonify
import pandas as pd
import numpy as np
import pymongo
from bson.objectid import ObjectId
import pytz
from thingview.forms import *
from thingview import app, db, LOCAL_TZ
from hashlib import md5


# some const
INIT_PWD_HASH = md5(b'initial').hexdigest()


# some functions
def get_user_lvl(username, password):
    # get user access level (0: no auth, 1-3:valid)
    u_info = db.users.find_one({'$query': {'user': username, 'pwd_hash': md5(password.encode()).hexdigest()}})
    if u_info:
        return u_info['level']
    else:
        return 0


def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        # check admin
        g.is_admin = session.get('user_lvl') == 3
        # check user level (0: no auth, 1-3:valid)
        if session.get('user_lvl') in [1, 2, 3]:
            return f(*args, **kwargs)
        else:
            session['username'] = ''
            return redirect(url_for('login'))

    return decorated


def requires_admin(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        # check admin
        if g.is_admin:
            return f(*args, **kwargs)
        else:
            return redirect(url_for('login'))

    return decorated


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    error = None
    if form.validate_on_submit():
        # get user level
        session['user_lvl'] = get_user_lvl(form.username.data,
                                           form.password.data)
        # check valid user level
        if session['user_lvl'] in [1, 2, 3]:
            session['username'] = form.username.data
            return redirect(url_for('root'))
        else:
            error = 'Votre nom d\'utilisateur ou votre mot de passe est invalide.'
    return render_template('login.html', form=form, error=error)


@app.route('/logout')
@requires_auth
def logout():
    session['user_lvl'] = 0
    return redirect(url_for('root'))


@app.route('/')
@requires_auth
def root():
    return redirect(url_for('devices'))


@app.route('/update_pwd', methods=['GET', 'POST'])
@requires_auth
def update_pwd():
    form = UpdatePwdForm()
    success = None
    error = None
    if form.validate_on_submit():
        # get user level
        db.users.update({'user': session['username']}, {'$set': {'pwd_hash': md5(form.password_1.data.encode()).hexdigest()}})
        success = 'mise à jour effectuée.'
    return render_template('update_pwd.html', form=form, success=success, error=error)


@app.route('/user/reset/<string:user_id>', methods=['GET', 'POST'])
@requires_auth
@requires_admin
def user_reset(user_id):
    rst_form = RstUserForm()
    success = None
    error = None
    # reset user with pwd as "initial"
    if rst_form.validate_on_submit():
        try:
            db.users.update({'_id': ObjectId(rst_form.user_id.data)}, {'$set': {'pwd_hash': INIT_PWD_HASH}})
        except pymongo.errors.PyMongoError:
            error = 'changement du mot de passe impossible'
        else:
            return redirect(url_for('users'))
    # define hidden field
    rst_form.user_id.data = user_id
    user = db.users.find_one({'$query': {'_id': ObjectId(user_id)}})
    return render_template('user_reset.html', user=user, rst_form=rst_form, success=success, error=error)


@app.route('/user/remove/<string:user_id>', methods=['GET', 'POST'])
@requires_auth
@requires_admin
def user_remove(user_id):
    rm_form = RmUserForm()
    error = None
    # remove user
    if rm_form.validate_on_submit():
        try:
            db.users.remove({'_id': ObjectId(rm_form.user_id.data)})
        except pymongo.errors.PyMongoError:
            error = 'impossible de supprimer l\'utilisateur'
        else:
            return redirect(url_for('users'))
    # define hidden field
    rm_form.user_id.data = user_id
    user = db.users.find_one({'$query': {'_id': ObjectId(user_id)}})
    return render_template('user_remove.html', user=user, rm_form=rm_form, error=error)


@app.route('/users', methods=['GET', 'POST'])
@requires_auth
@requires_admin
def users():
    add_form = AddUserForm()
    success = None
    error = None
    # add user with pwd as "initial"
    if add_form.validate_on_submit():
        try:
            db.users.insert({'user': add_form.username.data, 'pwd_hash': INIT_PWD_HASH, 'level': 1})
        except pymongo.errors.PyMongoError:
            error = 'ajout impossible'
        else:
            success = 'utilisateur ajouté'
    l_users = db.users.find({'$query': {}, '$orderby': {'user': 1}})
    return render_template('users.html', users=l_users, add_form=add_form, init_pwd_hash=INIT_PWD_HASH, success=success, error=error)


@app.route('/devices')
@requires_auth
def devices():
    l_dev = db.devices.find()
    return render_template('devices.html', devices=l_dev)


@app.route('/devices/id/<string:device_id>')
@requires_auth
def devices_id(device_id):
    l_dev = db.devices.find({'device_id': device_id})
    return render_template('devices.html', devices=l_dev)


@app.route('/map')
@requires_auth
def map():
    return render_template('map.html')


@app.route('/cnf_device/<string:device_id>', methods=['GET', 'POST'])
@requires_auth
@requires_admin
def cnf_device(device_id):
    # read device info
    dev = db.devices.find_one({'$query': {'device_id': device_id}})
    form = CnfDeviceForm()
    success = None
    error = None
    if form.validate_on_submit():
        # update device info
        d_update = dict()
        for fieldname, value in form.data.items():
            if fieldname in ['name']:
                d_update[fieldname] = value
            if dev.get('thing', '') == 'tx_pulse':
                if fieldname in ['tx_pulse_n1', 'tx_pulse_w1', 'tx_pulse_n2', 'tx_pulse_w2']:
                    d_update[fieldname] = value
        db.devices.update({'device_id': device_id}, {'$set': d_update})
        success = 'mise à jour effectuée.'
    return render_template('cnf_device.html', form=form, dev=dev, success=success, error=error)


@app.route('/things/tx_pulse/<string:device_id>')
@requires_auth
def thing_tx_pulse(device_id):
    # device data
    device = db.devices.find_one({'$query': {'device_id': device_id}})
    # convert raw data (raw to daily data)
    df_raw = pd.DataFrame(None, columns=['v1', 'v2'], dtype='float')
    for record in db.tx_pulse_raw.find({'$query': {'device_id': device_id}, '$orderby': {'msg_time': -1}}).limit(400):
        df_raw.loc[record['msg_time'].replace(tzinfo=pytz.utc).astimezone(LOCAL_TZ)] = [record['pulse_1'],
                                                                                        record['pulse_2']]
    # add weights
    df_raw['v1'] *= device.get('tx_pulse_w1', 1)
    df_raw['v2'] *= device.get('tx_pulse_w2', 10)
    # resample:
    # - for 5h gas time: use the max rx index value for 5h00 to 5h59 time window
    df_h = df_raw.resample('H', closed='left', label='left', how=np.max).interpolate().diff()
    df_j = df_h.resample(rule='24H', closed='left', label='left', base=6, how=np.sum)
    # web render
    return render_template('things/tx_pulse.html', device=device,
                           df_raw=df_raw[:3], df_h=df_h.sort(ascending=False)[:24], df_j=df_j.sort(ascending=False)[:7])


@app.route('/things/tx_temp/<string:device_id>')
@requires_auth
def thing_tx_temp(device_id):
    # device data
    device = db.devices.find_one({'$query': {'device_id': device_id}})
    # convert raw data (raw to daily data)
    df_t_raw = pd.DataFrame(None, columns=['temperature'], dtype='float')
    for record in db.tx_temp_raw.find({'$query': {'device_id': device_id}, '$orderby': {'msg_time': -1}}).limit(400):
        df_t_raw.loc[record['msg_time'].replace(tzinfo=pytz.utc).astimezone(LOCAL_TZ)] = [record['temperature']]
    # resample:
    df_j = pd.DataFrame()
    df_j['max'] = df_t_raw['temperature'].resample(rule='D', how=np.max)
    df_j['avg'] = df_t_raw['temperature'].resample(rule='D', how=np.mean)
    df_j['min'] = df_t_raw['temperature'].resample(rule='D', how=np.min)
    # web render
    return render_template('things/tx_temp.html', device=device,
                           df_raw=df_t_raw[:10], df_j=df_j.sort(ascending=False)[:7])


@app.route('/things_wgs84.json')
@requires_auth
def things_wgs84_json():
    l_thing = list()
    for dev in db.devices.find():
        l_thing.append({'device_id': dev.get('device_id', ''), 'name': dev.get('name', ''),
                        'lat': dev.get('lat', 0.0), 'lng': dev.get('lng', 0.0)})
    return jsonify(l_thing)
