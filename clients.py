from __future__ import division
import socket
import requests
import psutil
from autobahn.twisted.wamp import Application
from autobahn.twisted.util import sleep
from twisted.internet.defer import inlineCallbacks

app = Application('monitoring')
SERVER = '10.189.250.5'
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.connect(("8.8.8.8", 80))
app._params = {'name': socket.gethostname(), 'ip': s.getsockname()[0]}
app._socc={'lineNumber':'','editor':''}
s.close()
@app.signal('onjoined')
@inlineCallbacks

def called_on_joined():
    print("Connected")
    response = requests.post('http://10.189.248.225:8080/clients/', data={'1':'sejal','2':'keya'})
    if response.status_code == 200:
        app._socc.update(response.json())
    else:
        print("Could not retrieve configuration for client: {} ({})".format(response.reason, response.status_code))

@app.subscribe('keya.'+'6')

def update_configuration(args):
    app._socc.update(args)
    stats=args
    app.session.publish('clientstats', stats)

if __name__ == '__main__':
    app.run(url=u"ws://%s:8080/ws" % SERVER, debug=False, debug_wamp=False)
