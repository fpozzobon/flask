#! ../env/bin/python
# -*- coding: utf-8 -*-

import pytest
from unittest.mock import MagicMock
from flask import json
from tests.utils import createSong, createNSongs

def mockSongService(app):
  with app.app_context():
    songService = app.config['songService'] = MagicMock()
    return songService

def getResult(rv):
  return json.loads(rv.data)['result']

@pytest.mark.usefixtures("app")
class TestMainSongs:
  """ Test /songs route """

  def mockGetList(self, app, data, count):
    songService = mockSongService(app)
    songService.getList.return_value = data,count
    return songService

  def test_empty_db(self, app):
    """ Verify that we get a result from an empty database """
    # setUp
    testapp = app.test_client()
    songService = self.mockGetList(app, [], 0)

    rv = testapp.get('/songs')
    actual = getResult(rv)
    assert 0 == len(actual)
    assert [] == actual

  def test_default_args(self, app):
    """ Verify that we call songService with 20, 0 """
    # setup
    testapp = app.test_client()
    songService = self.mockGetList(app, [], 0)
    # test
    rv = testapp.get('/songs')
    # verification
    songService.getList.assert_called_with(20, 1)

  def test_with_arguments(self, app):
    """ Verify that we call songService with the right arguments """
    # setup
    testapp = app.test_client()
    songService = self.mockGetList(app, [], 0)
    # test
    rv = testapp.get('/songs?page_num=5&page_size=30')
    # verification
    songService.getList.assert_called_with(30, 5)

  def test_returns_list(self, app):
    """ Verify that we call songService with the right arguments """
    # setup
    testapp = app.test_client()
    expectedSongs = createNSongs(50)
    songService = self.mockGetList(app, expectedSongs, 0)
    # test
    rv = testapp.get('/songs')
    # verification
    actual = getResult(rv)
    assert expectedSongs == actual

  def test_returns_count_header(self, app):
    """ Verify that we get count in the header """
    # setup
    testapp = app.test_client()
    expectedCount = 452
    songService = self.mockGetList(app, [], expectedCount)
    # test
    rv = testapp.get('/songs')
    # verification
    actual = rv.headers['X-total-count']
    assert str(expectedCount) == actual

@pytest.mark.usefixtures("app")
class TestMainAverageDifficulty:
  """ Test /songs/avg/difficulty route """

  def mockAverageDifficulty(self, app, return_value):
    songService = mockSongService(app)
    songService.averageDifficulty.return_value = return_value
    return songService

  def test_difficulty_without_level(self, app):
    """ Verify that we get the difficulty without level param """
    # setup
    testapp = app.test_client()
    expectedAverage = 6
    songService = self.mockAverageDifficulty(app, expectedAverage)
    # test
    rv = testapp.get('/songs/avg/difficulty')
    # verification
    actual = getResult(rv)
    assert expectedAverage == actual
    songService.averageDifficulty.assert_called_with(None)

  def test_difficulty_with_level(self, app):
    """ Verify that we get the difficulty for a level param """
    # setup
    testapp = app.test_client()
    expectedAverage = 6
    expectedLevel = 5
    songService = self.mockAverageDifficulty(app, expectedAverage)
    # test
    rv = testapp.get('/songs/avg/difficulty/'+str(expectedLevel))
    # verification
    actual = getResult(rv)
    assert expectedAverage == actual
    songService.averageDifficulty.assert_called_with(expectedLevel)

@pytest.mark.usefixtures("app")
class TestMainSearch:
  """ Test /songs/search route """

  def mockSearch(self, app, return_value):
    songService = mockSongService(app)
    songService.search.return_value = return_value
    return songService

  def test_search_message(self, app):
    """ Verify that we get the songs filtered on a message """
    # setup
    testapp = app.test_client()
    expectedMessage = "A Message"
    expectedSongs = createNSongs(152)
    songService = self.mockSearch(app, expectedSongs)
    # test
    rv = testapp.get('/songs/search?message='+expectedMessage)
    # verification
    actual = getResult(rv)
    assert expectedSongs == actual
    songService.search.assert_called_with(expectedMessage)

  def test_search_message_without_arg(self, app):
    """ Verify that we get a 400 response if no message """
    # setup
    testapp = app.test_client()
    songService = self.mockSearch(app, None)
    # test
    rv = testapp.get('/songs/search')
    # verification
    assert "<Response streamed [400 BAD REQUEST]>" == str(rv)

@pytest.mark.usefixtures("app")
class TestMainRateSong:
  """ Test /songs/rating POST route """

  def createResult(self,updatedExisting):
    return {'update_result':{'raw_result':{'updatedExisting':updatedExisting}}}

  def mockRateSong(self, app, updatedExisting):
    songService = mockSongService(app)
    songService.rateSong.return_value = self.createResult(updatedExisting)
    return songService

  def test_rate_song_less_than_1(self, app):
    """ Verify that we don't call rateSong service """
    # setup
    testapp = app.test_client()
    songService = self.mockRateSong(app, True)
    # test
    actual = testapp.post('/songs/rating',data=dict(
        rating=0.314,
        song_id="any"
    ))
    # verification
    assert '<Response streamed [500 INTERNAL SERVER ERROR]>' == str(actual)
    songService.rateSong.assert_not_called()

  def test_rate_song_greater_than_5(self, app):
    """ Verify that we don't call rateSong service """
    # setup
    testapp = app.test_client()
    songService = self.mockRateSong(app, True)
    # test
    actual = testapp.post('/songs/rating',data=dict(
        rating=5.314,
        song_id="any"
    ))
    # verification
    assert '<Response streamed [500 INTERNAL SERVER ERROR]>' == str(actual)
    songService.rateSong.assert_not_called()

  def test_rate_song_error(self, app):
    """ Verify that we get the rating and call the service correctly """
    # setup
    testapp = app.test_client()
    songService = self.mockRateSong(app, False)
    # test
    actual = testapp.post('/songs/rating',data=dict(
        rating=1,
        song_id="any"
    ))
    # verification
    assert '<Response streamed [500 INTERNAL SERVER ERROR]>' == str(actual)

  def test_rate_song_ok(self, app):
    """ Verify that we get the rating and call the service correctly """
    # setup
    testapp = app.test_client()
    expectedRating = 4.56
    expectedId = "anyId"
    songService = self.mockRateSong(app, True)
    # test
    actual = testapp.post('/songs/rating',data=dict(
        rating=expectedRating,
        song_id=expectedId
    ))
    # verification
    songService.rateSong.assert_called_with(expectedId,expectedRating)

@pytest.mark.usefixtures("app")
class TestMainRating:
  """ Test /songs/avg/rating/<string:song_id> route """

  def mockRating(self, app, return_value):
    songService = mockSongService(app)
    songService.rating.return_value = return_value
    return songService

  def test_rating(self, app):
    """ Verify that we get the rating and call the service correctly """
    # setup
    testapp = app.test_client()
    expectedRating = 4.56
    expectedId = "anyId"
    songService = self.mockRating(app, expectedRating)
    # test
    rv = testapp.get('/songs/avg/rating/'+expectedId)
    # verification
    actual = getResult(rv)
    assert expectedRating == actual
    songService.rating.assert_called_with(expectedId)
