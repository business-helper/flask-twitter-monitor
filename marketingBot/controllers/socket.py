from datetime import datetime
from flask import request
from flask_socketio import SocketIO

from marketingBot import app
from marketingBot.models.User import db, User
from marketingBot.helpers.wrapper import session_required

socketio = SocketIO(app)

io_clients = {}


def io_notify_user(user_id, event, args):
  if str(user_id) not in io_clients:
    return False
  if str(user_id) in io_clients:
    return socketio.emit(event, args, room = io_clients[str(user_id)])


def messageReceived(method=['GET', 'POST']):
  print('message was received!')


@socketio.on('connect')
@session_required
def socket_connected(self):
  print('[Socket][Connected]', request.sid, self)
  
  str_user_id = str(self.id)
  io_clients[str_user_id] = request.sid #request.namespace
  # print('[IO Clients]', io_clients)

  # user = User.query.filter_by(id=self.id).first()
  # user.socket_id = request.sid
  # user.updated_at = datetime.utcnow()
  # db.session.commit()


@socketio.on('disconnect')
@session_required
def socket_disconnect(self):
  print('[Socket][Disconnected]', self)

@socketio.on('PING')
def handle_my_event(json, methods=['GET', 'POST']):
  print('recieved my event: ' + str(json))
  socketio.emit('PONG', json, callback=messageReceived)
