from flask import request, jsonify

from marketingBot.models.Notification import db, Notification
from marketingBot.controllers.api import api
from marketingBot.helpers.wrapper import session_required

@api.route('/notifications/<id>', methods=['DELETE'])
@session_required
def delete_notification_by_id(self, id):
  notification = db.session.query(Notification).filter_by(id=id).one()
  if not notification:
    return jsonify({
      "status": False,
      "message": 'Bot does not exist!',
    })
  db.session.delete(notification)
  db.session.commit()

  return jsonify({
    "status": True,
    "message": "You deleted a notification!",
  })
