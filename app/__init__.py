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
@click.option('--nbloops', default=1, help='number of loops through the file to load')
def initdb(nbloops):
    """Initialize the database."""
    click.echo('Init the db')
    # populate the songs from static/songs.json if song collection is empty
    song = mongo.db.songs
    if song.count() == 0:
      for i in range(nbloops):
        with current_app.open_resource('static/songs.json', mode="r") as f:
          song.insert_many(json.loads(line) for line in f)
      click.echo("Created " + str(song.count()) + "songs.")
      # Note we could probably put that to unique, also the weight is 10:1 for artist
      song.create_index( [('artist', 'text'), ('title', 'text')],
                        name="artist and title index", unique=False, weights={'artist': 10 } )
    else:
      click.echo("Songs collection already contains data, please clean it first.")

@app.cli.command()
def cleandb():
    """Remove songs collection."""
    click.echo('Remove songs collection.')
    mongo.db.songs.drop()

from app import routes
