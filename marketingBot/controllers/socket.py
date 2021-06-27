from flask import request
from flask_socketio import SocketIO

from marketingBot import app
from marketingBot.helpers.wrapper import session_required

socketio = SocketIO(app)

def messageReceived(method=['GET', 'POST']):
  print('message was received!')

@socketio.on('connect')
@session_required
def socket_connected(self):
  print('[Socket][Connected]', request.sid, self)


@socketio.on('PING')
def handle_my_event(json, methods=['GET', 'POST']):
  print('recieved my event: ' + str(json))
  socketio.emit('PONG', json, callback=messageReceived)
