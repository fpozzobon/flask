import os
from flask import Flask, json, current_app, g
from flask_pymongo import PyMongo
from app.song_service import SongService

DEFAULT_DATABASE_URL = 'mongodb://localhost:27017/flask'

app = Flask(__name__)

def configureDatabase():
  app.config['MONGO_URI'] = os.environ.get('FLASK_API_DB_URL', DEFAULT_DATABASE_URL)
  app.logger.info('Connecting to the database : %s', app.config['MONGO_URI'])
  return PyMongo(app)

with app.app_context():
  mongo = configureDatabase()
  songService = SongService(mongo.db.songs, app.logger)

from app import initdb
from app import routes
