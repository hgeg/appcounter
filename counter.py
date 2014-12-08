from flask import Flask, Request
from redis import StrictRedis as R
import time, json
import settings

app = Flask(__name__)
rdb = R('localhost',6379,3)

#helper functions

#return all apps
def apps(rdb): return rdb.zrange('counter.apps',10)

#return all action types for given app
def types(rdb,app): 
    alen = rdb.getset('counter.%s.len'%(app),0)
    return rdb.zrange('counter.%s.actions'%(app),alen)

#return all action objects
def actions(rdb,app,action):
    alen = rdb.getset('counter.%s.%s.len'%(app,action),0)
    return rdb.lrange('counter.%s.%s.objects'%(app,action),alen)

#add an app to system
def add_app(rdb,app):
    rdb.zadd('counter.apps',app)
    rdb.zadd('counter.

#add an action to app
def add_action(rdb,app,action)
    rdb.

def filter_by(app='all',timeframe=None,action=all): pass

@app.route('/counter/send/')
def send(): pass

@app.route('/counter/dashboard/')
def dashboard(): pass
