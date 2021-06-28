const EVENT = {
  NEW_TWEET_FOUND: 'NEW_TWEET_FOUND',
}



var socket = io.connect('/');

socket.on( 'connect', function() {
  console.log('[SocketID]', socket.id)
  // socket.emit( 'PING', {
  //   data: 'User Connected'
  // })

  // socket.emit( 'PING', {
  //   user_name : 'Aleks',
  //   message : 'Hello Flask Socket'
  // })
})

// socket.on('PONG', args => {
//   console.log('[EVENT][PONG]', args)
// })

socket.on(EVENT.NEW_TWEET_FOUND, args => {
  console.log('[New Tweet]', args);
  toastr.info(args.translated, `${args.bot} - New tweet from @${args.user_name}`)
})
