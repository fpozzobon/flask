import click
import flask_pymongo
from flask import json, Flask
from app.db_config import configureDatabase

app = Flask(__name__)

with app.app_context():
    mongo = configureDatabase(app)


def createIndexes(song):
    click.echo('Creating indexes')
    # Note we could probably put that to unique, also the weight is 10:1 for artist
    song.create_index([('artist', 'text'), ('title', 'text')],
                      name="artist and title index",
                      unique=False,
                      weights={'artist': 10})
    song.create_index([('level', flask_pymongo.ASCENDING)],
                      name="level index",
                      unique=False)


@app.cli.command()
@click.option('--nbloops', default=1, help='number of loops through the file to load')
def initdb(nbloops):
    """Initialize the database."""
    click.echo('Init the db')
    # populate the songs from static/songs.json if song collection is empty
    song = mongo.db.songs
    if song.count() == 0:
        for i in range(nbloops):
            with app.open_resource('static/songs.json', mode="r") as f:
                song.insert_many(json.loads(line) for line in f)
        click.echo("Created " + str(song.count()) + "songs.")
        createIndexes(song)
    else:
        click.echo("Songs collection already contains data, please clean it first.")


@app.cli.command()
def cleandb():
    """Remove songs collection."""
    click.echo('Remove songs collection.')
    mongo.db.songs.drop()
