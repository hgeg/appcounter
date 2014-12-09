from flask import Flask,request,jsonify,render_template,send_from_directory
#from flup.server.fcgi import WSGIServer
from redis import StrictRedis as R
import json, hashlib, datetime, time, uuid, sys
import settings

app = Flask(__name__, static_url_path='')
rdb = R('localhost',6379,3)
t_timestamp = lambda: int(time.time())
t_ttd = lambda t: datetime.datetime.fromtimestamp(int(t)).strftime('%d/%m/%Y')

#database functions

#return all apps
def db_apps(rdb): return rdb.smembers('counter.apps')

#return all action types for given app
def db_types(rdb,app): return rdb.smembers('counter.%s.actions'%(app))

#return all action objects
def db_actions(rdb,app,action):
    alen = rdb.get('counter.%s.%s.len'%(app,action)) or 0
    return rdb.lrange('counter.%s.%s.objects'%(app,action),0,alen)

#add an app to system
def db_add_app(rdb,app):
    rdb.sadd('counter.apps',app)
    rdb.sadd('counter.%s.actions'%(app),'init')
    rdb.srem('counter.%s.actions'%(app),'init')

#add an action to app
def db_add_action(rdb,app,action,obj):
    data = json.dumps(obj)
    if app not in db_apps(rdb): 
        rdb.sadd('counter.apps',app)
    rdb.sadd('counter.%s.actions'%(app),action)
    rdb.rpush('counter.%s.%s.objects'%(app,action),data)
    rdb.incr('counter.%s.%s.len'%(app,action))

def db_get_ticket(rdb,udid):
    ticket = rdb.get('counter.ticket.%s'%udid)
    return  ticket if ticket else ''

def db_set_ticket(rdb,udid):
    new = uuid.uuid4()
    rdb.set('counter.ticket.%s'%udid,new)
    return new

def db_filter_by(rdb,app,timeframe=None,action='all',udid=None): 
    if app not in db_apps(rdb):
        return jsonify(data=False, error='app "%s" not found'%app)
    available = db_types(rdb, app)
    if action == 'all':
        used = available
    elif not all(lambda e: e in available, action):
        return jsonify(data=False, error='action "%s" not found in "%s"'%(action,app))
    else: used = [action]
    data = []
    for k in used:
        serie = {'label':k}
        objects = [json.loads(e) for e in db_actions(rdb,app,k) if timeframe[0]<json.loads(e)['timestamp']<timeframe[1]]
        dsub = {}
        for o in objects:
            day = t_ttd(o['timestamp'])
            dsub.update({day:dsub.get(day,0)+1})
        values = [{'x':k, 'y':v} for k,v in dsub.iteritems()]
        serie.update({"values":values})
        data.append(serie)
    
    return jsonify({'data':data,'error':False,'actions':[e['label'] for e in data]})

#web app methods
@app.route('/counter/send/',methods=['POST'])
def receive_action():
    post = request.form
    try:
        app = post['app']
        action = post['action']
        api_key = post['api_key']
        timestamp = int(post['timestamp'])
        signature = post['signature']
        udid = post['udid']
        ticket = post['ticket']
    except Exception as e:
        return jsonify(data=False,error=e.message)
    try:
        metadata = post['metadata']
    except: metadata = ''


    #check signature
    if api_key not in settings.keys:
        return jsonify(data=False, error='invalid client')
    if timestamp < t_timestamp() - 30:
        return jsonify(data=False, error='request too old')
    if not ticket == db_get_ticket(rdb,udid):
        return jsonify(data=False, error='invalid request')
    generated = hashlib.sha1('%s&%s&%s&%d&%s&%s&%s'%(app,action,udid,timestamp,ticket,api_key,settings.keys[api_key])).hexdigest()
    if not generated==signature:
        return jsonify(data=False, error='signature does not match')
    new_ticket = db_set_ticket(rdb, udid)
    obj = {'UDID':udid,'timestamp':timestamp,'type':action,'metadata':metadata}
    db_add_action(rdb,app,action,obj)
    return jsonify(data=True,error=False,ticket=new_ticket)

@app.route('/counter/dashboard/',methods=['GET'])
@app.route('/counter/dashboard/<app>/',methods=['POST'])
def dashboard(app=None):
    if request.method == 'POST':
        try:
            post = request.form
            start = post.get('start',None) or t_timestamp() - 259200
            end = post.get('end',None) or t_timestamp() + 345600
            timeframe = start,end
            data = db_filter_by(rdb,app,timeframe,post['actions'] if 'actions' in post and len(post['actions'])>0 else 'all')
            return data
        except Exception as e:
            exc_type, exc_obj, tb = sys.exc_info()
            lineno = tb.tb_lineno
            return jsonify(data=False,error=e.message,line=lineno)
    else:
        if app and app in db_apps(rdb):
            return render_template('plot.html',actions=db_types(rdb,app),apps=db_apps(rdb))
        else:
            return render_template('plot.html',apps=db_apps(rdb))

@app.route('/counter/static/<path:path>')
def static_proxy(path):
    return send_from_directory('./static', path)

def main():
  app.run('0.0.0.0',5000,debug=True)

if __name__ == '__main__': main()
