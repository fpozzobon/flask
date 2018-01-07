import pytest
from flask import Flask
from app.controllers.main import main as mainTest
from app.extensions import cache
import mongomock
from app.song_service import SongService
from unittest.mock import MagicMock


@pytest.fixture
def main(mocker):
    songService = mocker.patch('app.controllers.main.songService')
    app = Flask(__name__)
    app.register_blueprint(mainTest)
    testapp = app.test_client()
    return testapp, songService


@pytest.fixture
def song_service(mocker):
    app = Flask(__name__)
    app.testing = True
    cache.init_app(app, config={'CACHE_TYPE': 'simple'})
    mockedMongoClient = mongomock.MongoClient()
    mockedSongCollection = mockedMongoClient.db.songs
    tested = SongService()
    tested.init(mockedSongCollection, MagicMock())
    mockedCache = mocker.patch('app.song_service.cache')
    return tested, mockedSongCollection, mockedCache
