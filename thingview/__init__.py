import os
from flask import Flask
from pymongo import MongoClient
import pytz

# some const
LOCAL_TZ = pytz.timezone('Europe/Paris')


# init mongo
db = MongoClient().iot


# some class
class LocalFlask(Flask):
    # force anonymous server name
    def process_response(self, response):
        response.headers['server'] = 'ThingView Flask server'
        super(LocalFlask, self).process_response(response)
        return (response)


# some functions
def datetimefilter(dt, fmt='%Y-%m-%d %H:%M:%S'):
    utc_dt = pytz.utc.localize(dt)
    return utc_dt.astimezone(LOCAL_TZ).strftime(fmt)


# Flask app
app = LocalFlask(__name__)
app.jinja_env.filters['datetimefilter'] = datetimefilter
app.secret_key = os.environ.get("THINGVIEW_SECRET_KEY", os.urandom(12))

# load all Flask routes
from thingview import routes
