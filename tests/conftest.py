import pytest
from flask import Flask
from app.controllers.main import main as mainTest


@pytest.fixture
def main(mocker):
    songService = mocker.patch('app.controllers.main.songService')
    app = Flask(__name__)
    app.register_blueprint(mainTest)
    testapp = app.test_client()
    return testapp, songService
