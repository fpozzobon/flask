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

@pytest.mark.usefixtures("main")
class TestMainSongs:
  """ Test /songs route """

  def mockGetList(self, songService, data, count):
    songService.getList.return_value = data,count

  def test_empty_db(self, main):
    """ Verify that we get a result from an empty database """
    # setUp
    testapp, songService = main
    self.mockGetList(songService, [], 0)

    rv = testapp.get('/songs')
    actual = getResult(rv)
    assert 0 == len(actual)
    assert [] == actual

  def test_default_args(self, main):
    """ Verify that we call songService with 20, 0 """
    # setup
    testapp, songService = main
    self.mockGetList(songService, [], 0)
    # test
    rv = testapp.get('/songs')
    # verification
    songService.getList.assert_called_with(20, 1)

  def test_with_arguments(self, main):
    """ Verify that we call songService with the right arguments """
    # setup
    testapp, songService = main
    self.mockGetList(songService, [], 0)
    # test
    rv = testapp.get('/songs?page_num=5&page_size=30')
    # verification
    songService.getList.assert_called_with(30, 5)

  def test_returns_list(self, main):
    """ Verify that we call songService with the right arguments """
    # setup
    testapp, songService = main
    expectedSongs = createNSongs(50)
    self.mockGetList(songService, expectedSongs, 0)
    # test
    rv = testapp.get('/songs')
    # verification
    actual = getResult(rv)
    assert expectedSongs == actual

  def test_returns_count_header(self, main):
    """ Verify that we get count in the header """
    # setup
    testapp, songService = main
    expectedCount = 452
    self.mockGetList(songService, [], expectedCount)
    # test
    rv = testapp.get('/songs')
    # verification
    actual = rv.headers['X-total-count']
    assert str(expectedCount) == actual

@pytest.mark.usefixtures("main")
class TestMainAverageDifficulty:
  """ Test /songs/avg/difficulty route """

  def mockAverageDifficulty(self, songService, return_value):
    songService.averageDifficulty.return_value = return_value

  def test_difficulty_without_level(self, main):
    """ Verify that we get the difficulty without level param """
    # setup
    testapp, songService = main
    expectedAverage = 6
    self.mockAverageDifficulty(songService, expectedAverage)
    # test
    rv = testapp.get('/songs/avg/difficulty')
    # verification
    actual = getResult(rv)
    assert expectedAverage == actual
    songService.averageDifficulty.assert_called_with(None)

  def test_difficulty_with_level(self, main):
    """ Verify that we get the difficulty for a level param """
    # setup
    testapp, songService = main
    expectedAverage = 6
    expectedLevel = 5
    self.mockAverageDifficulty(songService, expectedAverage)
    # test
    rv = testapp.get('/songs/avg/difficulty/'+str(expectedLevel))
    # verification
    actual = getResult(rv)
    assert expectedAverage == actual
    songService.averageDifficulty.assert_called_with(expectedLevel)

@pytest.mark.usefixtures("main")
class TestMainSearch:
  """ Test /songs/search route """

  def mockSearch(self, songService, return_value):
    songService.search.return_value = return_value

  def test_search_message(self, main):
    """ Verify that we get the songs filtered on a message """
    # setup
    testapp, songService = main
    expectedMessage = "A Message"
    expectedSongs = createNSongs(152)
    self.mockSearch(songService, expectedSongs)
    # test
    rv = testapp.get('/songs/search?message='+expectedMessage)
    # verification
    actual = getResult(rv)
    assert expectedSongs == actual
    songService.search.assert_called_with(expectedMessage)

  def test_search_message_without_arg(self, main):
    """ Verify that we get a 400 response if no message """
    # setup
    testapp, songService = main
    self.mockSearch(songService, None)
    # test
    rv = testapp.get('/songs/search')
    # verification
    assert "<Response streamed [400 BAD REQUEST]>" == str(rv)

@pytest.mark.usefixtures("main")
class TestMainRateSong:
  """ Test /songs/rating POST route """

  def createResult(self,updatedExisting):
    return {'update_result':{'raw_result':{'updatedExisting':updatedExisting}}}

  def mockRateSong(self, songService, updatedExisting):
    songService.rateSong.return_value = self.createResult(updatedExisting)

  def test_rate_song_less_than_1(self, main):
    """ Verify that we don't call rateSong service """
    # setup
    testapp, songService = main
    self.mockRateSong(songService, True)
    # test
    actual = testapp.post('/songs/rating',data=dict(
        rating=0.314,
        song_id="any"
    ))
    # verification
    assert '<Response streamed [500 INTERNAL SERVER ERROR]>' == str(actual)
    songService.rateSong.assert_not_called()

  def test_rate_song_greater_than_5(self, main):
    """ Verify that we don't call rateSong service """
    # setup
    testapp, songService = main
    self.mockRateSong(songService, True)
    # test
    actual = testapp.post('/songs/rating',data=dict(
        rating=5.314,
        song_id="any"
    ))
    # verification
    assert '<Response streamed [500 INTERNAL SERVER ERROR]>' == str(actual)
    songService.rateSong.assert_not_called()

  def test_rate_song_error(self, main):
    """ Verify that we get the rating and call the service correctly """
    # setup
    testapp, songService = main
    self.mockRateSong(songService, False)
    # test
    actual = testapp.post('/songs/rating',data=dict(
        rating=1,
        song_id="any"
    ))
    # verification
    assert '<Response streamed [500 INTERNAL SERVER ERROR]>' == str(actual)

  def test_rate_song_ok(self, main):
    """ Verify that we get the rating and call the service correctly """
    # setup
    testapp, songService = main
    expectedRating = 4.56
    expectedId = "anyId"
    self.mockRateSong(songService, True)
    # test
    actual = testapp.post('/songs/rating',data=dict(
        rating=expectedRating,
        song_id=expectedId
    ))
    # verification
    songService.rateSong.assert_called_with(expectedId,expectedRating)

@pytest.mark.usefixtures("main")
class TestMainRating:
  """ Test /songs/avg/rating/<string:song_id> route """

  def mockRating(self, songService, return_value):
    songService.rating.return_value = return_value

  def test_rating(self, main):
    """ Verify that we get the rating and call the service correctly """
    # setup
    testapp, songService = main
    expectedRating = 4.56
    expectedId = "anyId"
    self.mockRating(songService, expectedRating)
    # test
    rv = testapp.get('/songs/avg/rating/'+expectedId)
    # verification
    actual = getResult(rv)
    assert expectedRating == actual
    songService.rating.assert_called_with(expectedId)
