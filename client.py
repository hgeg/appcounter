import requests,time,json,hashlib

timestamp = lambda: int(time.time())
server = 'http://localhost:5000'
key = 'test'
secret = 'secret'
ticket = ''
udid = 'TESTDEVICE'

signature = lambda app,action,udid,timestamp,ticket,api_key,secret: hashlib.sha1('%s&%s&%s&%d&%s&%s&%s'%(app,action,udid,timestamp,ticket,api_key,secret)).hexdigest()

def send(app,action):
    global ticket
    t = timestamp()
    s = signature(app,action,udid,t,ticket,key,secret)
    data = {'app':app, 'action':action, 'udid':udid, 'timestamp':t, 'signature':s, 'api_key':key, 'ticket': ticket}
    response = requests.post('%s/counter/send/'%server,data=data).text
    try:
        j = json.loads(response)
        ticket = j['ticket']
        print j
    except:
      print response

def data(app,start=None,end=None):
    data = {}
    response = requests.post('%s/counter/dashboard/%s/'%(server,app),data=data).text
    try:
        j = json.loads(response)
        print j
    except:
      print response
