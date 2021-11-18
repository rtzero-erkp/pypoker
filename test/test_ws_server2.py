import json
import datetime
import time
from geventwebsocket import WebSocketApplication
from flask_sockets import Sockets
from flask import Flask, Blueprint

# ws = Blueprint(r'ws', __name__)
app = Flask(__name__)
sockets = Sockets(app)
# sockets.register_blueprint(ws, url_prefix=r'/')


@app.route('/')
def index():
    return 'hello'


@sockets.route('/poker/texas-holdem')
def test(ws):
    print("test")
    while not ws.closed:
        msg = ws.receive()
        print(f'i received:{msg}')
        if msg:
            now = datetime.datetime.now().isoformat()
            ws.send(now)
            print(f'i sent:{now}')
            time.sleep(1)


if __name__ == "__main__":
    from gevent import pywsgi
    from geventwebsocket.handler import WebSocketHandler
    server = pywsgi.WSGIServer(
        ('0.0.0.0', 5000), application=app, handler_class=WebSocketHandler)
    print('server started')
    server.serve_forever()

# class EchoApplication(WebSocketApplication):

#     def on_open(self):
#         print(u'有人连接啦')
#         self.ws.send(u'connection success')

#     def on_message(self, message):
#         try:
#             if isinstance(message, dict):
#                 message = json.dumps(message)
#             print(u'接收数据:%s' % (message))
#             message = json.loads(message)
#             msg_type = message["type"]
#         except:
#             self.send_error('unknow message!')
#             return

#         # sid = request.sid

#         # return
#         if msg_type == 'heart_msg':
#             self.handle_online_device(message)
#             return
#         if msg_type == 'authentication':
#             self.ws.send(json.dumps({}))
#         else:
#             self.send_error(u'身份认证失败', operation=u'authentication')
#             self.ws.close()
#         return

#     def on_close(self, reason):
#         print(u'有人断开了,hhhhhhh')


# if __name__ == "__main__":
#     from werkzeug.debug import DebuggedApplication
#     from geventwebsocket import Resource, WebSocketServer
#     WebSocketServer(('0.0.0.0', 5000),
#                     Resource([('/', EchoApplication),
#                              ('^/.*', DebuggedApplication(app))]),
#                     debug=False).serve_forever()
