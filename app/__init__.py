from flask import Flask, json, current_app, g
from app.song_service import SongService
from app.controllers.main import main
from app.db_config import configureDatabase

def create_app():
  app = Flask(__name__)

  with app.app_context():
    mongo = configureDatabase(app)
    current_app.config['songService'] = SongService(mongo.db.songs, app.logger)

    # register our blueprints
    app.register_blueprint(main)

  return app
