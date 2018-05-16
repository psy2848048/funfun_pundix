# -*- coding: utf-8 -*-
from app import app
from gevent.wsgi import WSGIServer

https = WSGIServer(('0.0.0.0', app.config['PORT']), app, keyfile=app.config['SSL_KEY'], certfile=app.config['SSL_CERT'])
https.serve_forever()

# http = WSGIServer(('0.0.0.0', 5000), app)
