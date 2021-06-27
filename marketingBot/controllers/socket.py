from datetime import datetime
from flask import request
from flask_socketio import SocketIO, emit

from marketingBot import app
from marketingBot.models.User import db, User
from marketingBot.helpers.wrapper import session_required

socketio = SocketIO(app)

io_clients = {}

def io_notify_user(user_id, event, args):
  if str(user_id) not in io_clients:
    return False
  # return io_clients[str(user_id)].emit(event, args)
  print('[SocketId]', io_clients[str(user_id)])
  return socketio.emit(event, args, room = io_clients[str(user_id)])

def messageReceived(method=['GET', 'POST']):
  print('message was received!')

@socketio.on('connect')
@session_required
def socket_connected(self):
  print('[Socket][Connected]', request.sid, self)
  
  str_user_id = str(self.id)
  io_clients[str_user_id] = request.sid #request.namespace
  print('[IO Clients]', io_clients)

  user = User.query.filter_by(id=self.id).first()
  user.socket_id = request.sid
  user.updated_at = datetime.utcnow()
  db.session.commit()

# @socketio.on('connected')
# @session_required
# def socket_connectedd(self):
#   io_clients[str(self.id)] = request.namespace
#   print('[Io Clinet][Connected]', io_clients)


@socketio.on('PING')
def handle_my_event(json, methods=['GET', 'POST']):
  print('recieved my event: ' + str(json))
  socketio.emit('PONG', json, callback=messageReceived)
