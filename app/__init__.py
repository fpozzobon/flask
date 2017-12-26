from flask import Flask, json, current_app
from flask_pymongo import PyMongo
import sys

app = Flask(__name__)

DEFAULT_DATABASE_URL = 'mongodb://localhost:27017/flask'
def configureDatabase():
  app.config['MONGO_URI'] = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_DATABASE_URL
  return PyMongo(app)

# populate the songs from static/songs.json if song collection is empty
with app.app_context():
    mongo = configureDatabase()

    song = mongo.db.songs
    # TODO move it
    # if song.count() == 0:
        # with current_app.open_resource('static/songs.json', mode="r") as f:
            # for line in f:
                # song.insert(json.loads(line))

from app import routes
