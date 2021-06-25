from flask import request, current_app, jsonify
from datetime import datetime

# from marketingBot.models import db
from marketingBot.models.AppKey import db, AppKey
from marketingBot.controllers.api import api
# from marketingBot.helpers.common import timestamp

@api.route('/ping', methods=['GET'])
def api_ping():
  return jsonify({
    "status": True,
    "message": "pong"
  })


@api.route('/api-apps/<id>', methods=['GET'])
def get_api_app_by_id(id):
  api_key = AppKey.query.filter_by(id=id).first()
  return jsonify({
    "status": True,
    "message": "success",
    "data": api_key.to_dict(),
  })

@api.route('/api-apps/<id>', methods=['PUT'])
def update_api_app_by_id(id):
  payload = dict(request.get_json())
  print('[Payload]', payload)
  api_key = AppKey.query.filter_by(id=id).first()
  if not api_key:
    return jsonify({
      "status": False,
      "message": "API app does not exist!"
    })

  api_key.consumer_key = payload['consumer_key']
  api_key.consumer_secret = payload['consumer_secret']
  api_key.access_token = payload['access_token']
  api_key.access_token_secret = payload['access_token_secret']
  api_key.valid = payload['valid']
  api_key.name = payload['name']
  api_key.updated_at = datetime.utcnow()

  db.session.merge(api_key)
  db.session.flush()
  db.session.commit()
  return jsonify({
    "status": True,
    "message": "Data has been updated successfully!",
    "data": api_key.to_dict(),
  })

@api.route('/api-apps/<id>', methods=['DELETE'])
def delete_api_app_by_id(id):
  api_key = AppKey.query.filter_by(id=id).one()
  if not api_key:
    return jsonify({
      "status": False,
      "message": 'Api app does not exist!',
    })
  
  db.session.delete(api_key)
  # AppKey.query.filter_by(id=id).delete()
  # db.session.flush()
  db.session.commit()
  return jsonify({
    "status": True,
    "message": "Api app has been deleted!",
  })