
var socket = io.connect('/');

socket.on( 'connect', function() {
  console.log('[SocketID]', socket.id)
  socket.emit( 'PING', {
    data: 'User Connected'
  })

  socket.emit( 'PING', {
    user_name : 'Aleks',
    message : 'Hello Flask Socket'
  })
})

socket.on('PONG', args => {
  console.log('[EVENT][PONG]', args)
})
