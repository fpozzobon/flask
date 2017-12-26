import os
import click
from flask import Flask, json, current_app, g
from flask_pymongo import PyMongo
import sys

DEFAULT_DATABASE_URL = 'mongodb://localhost:27017/flask'

app = Flask(__name__)

def configureDatabase():
  app.config['MONGO_URI'] = os.environ.get('FLASK_API_DB_URL', DEFAULT_DATABASE_URL)
  app.logger.info('Connecting to the database : %s', app.config['MONGO_URI'])
  return PyMongo(app)

with app.app_context():
  mongo = configureDatabase()

@app.cli.command()
def initdb():
    """Initialize the database."""
    click.echo('Init the db')
    # populate the songs from static/songs.json if song collection is empty
    song = mongo.db.songs
    if song.count() == 0:
      with current_app.open_resource('static/songs.json', mode="r") as f:
        for line in f:
          song.insert(json.loads(line))

from app import routes
