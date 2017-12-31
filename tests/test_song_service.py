#! ../env/bin/python
# -*- coding: utf-8 -*-

import pytest
import unittest
from unittest.mock import MagicMock
import mongomock
import flask
import sys
mockedCache=MagicMock()
sys.modules['app.extensions.cache']=mockedCache
from app.song_service import SongService
from app.exceptions import SongNotFoundException, ResourceNotFoundException
from tests.utils import insertNSongsInDb, createSong
import bson

class TestService(unittest.TestCase):
  """ Test Service """
  def setUp(self):
    self.app = flask.Flask(__name__)
    self.app.testing = True

class TestSongServiceWithMongoMock(TestService):
  """ Test Song Service using mongo mock """
  def setUp(self):
    super().setUp()
    self.song_id="5a44f39191f4196576cb1eb2"
    mockedMongoClient=mongomock.MongoClient()
    self.mockedSongCollection=mockedMongoClient.db.songs
    self.tested = SongService(self.mockedSongCollection, MagicMock())
  def tearDown(self):
    super().tearDown()

class TestSongServiceWithMagicMock(TestService):
  """ Test Song Service using Magic mock """
  def setUp(self):
    super().setUp()
    self.mockedSongCollection=MagicMock()
    self.tested = SongService(self.mockedSongCollection, MagicMock())
  def tearDown(self):
    super().tearDown()

class TestGetList(TestSongServiceWithMongoMock):
  """ Get List """
  def test_get_list_with_empty_db(self):
    """ Verify that we get an empty result from the database """
    # test
    with self.app.app_context():
      data, count = self.tested.getList(10, 20)
    # verification
    assert [] == data
    assert 0 == count

  def test_get_list_with_populated_db(self):
    """ Verify that we get a result from the database """
    # result
    expectedResult=insertNSongsInDb(500, self.mockedSongCollection)
    # test
    with self.app.app_context():
      data, count = self.tested.getList(10, 1)
    # verification
    assert expectedResult[0:10] == data
    assert 500 == count

  def test_get_list_with_populated_db_pagination(self):
    """ Verify that we get a result from the database """
    # result
    expectedCount=500
    expectedPageSize=20
    expectedPageNum=10
    expectedResult=insertNSongsInDb(expectedCount, self.mockedSongCollection)
    # test
    with self.app.app_context():
      data, count = self.tested.getList(expectedPageSize, expectedPageNum)
    # verification
    expectedIndex=(expectedPageSize*(expectedPageNum-1))
    assert expectedResult[expectedIndex:expectedIndex+expectedPageSize] == data
    assert expectedCount == count

class TestAverageDifficulty(TestSongServiceWithMongoMock):
  """ Get AverageDifficulty """
  def test_get_average_difficulty_with_empty_db(self):
    """ Verify that we get an empty result from the database """
    # test
    with self.app.app_context():
      actual = self.tested.averageDifficulty()
    # verification
    assert None == actual

  # Unable to test the other tests cases as $avg is not implemented in mongomock

class TestSearch(TestSongServiceWithMongoMock):
  """ Search """
  def test_search_with_empty_db(self):
    """ Verify that we get an empty result from the database """
    # test
    with self.app.app_context():
      actual = self.tested.search("anymessage")
    # verification
    assert [] == actual

  def test_search_on_title(self):
    """ Verify that we get a result from the database """
    # result
    expectedResult=insertNSongsInDb(5, self.mockedSongCollection)
    # test
    with self.app.app_context():
      actual = self.tested.search("title1")
    # verification
    assert [expectedResult[1]] == actual

  def test_search_on_artist(self):
    """ Verify that we get a result from the database """
    # result
    expectedResult=insertNSongsInDb(10, self.mockedSongCollection)
    # test
    with self.app.app_context():
      actual = self.tested.search("artist5")
    # verification
    assert [expectedResult[5]] == actual

  def test_search_on_partial_word(self):
    """ Verify that we get a result from the database """
    # result
    expectedResult=insertNSongsInDb(10, self.mockedSongCollection)
    # test
    with self.app.app_context():
      actual = self.tested.search("art")
    # verification
    assert expectedResult == actual

class TestRateSong(TestSongServiceWithMongoMock):
  """ Rate Song """
  def test_rate_with_empty_db(self):
    """ Verify that we get an exception SongNotFoundException """
    # test
    with self.app.app_context():
      self.assertRaises(SongNotFoundException,
                        self.tested.rateSong,
                        self.song_id,
                        123)

  def insert_valid_test_case(self,ratings=None):
    # setup
    songToInsert={'_id':bson.ObjectId(self.song_id)}
    if not ratings == None:
      songToInsert['ratings']=ratings
    self.mockedSongCollection.insert(songToInsert)
    return songToInsert

  def verify_rate(self,ratings=None):
    # setup
    expectedRating=123.3
    songToInsert=self.insert_valid_test_case(ratings)
    # test
    with self.app.app_context():
      actual = self.tested.rateSong(self.song_id,expectedRating)
      updatedSong=self.mockedSongCollection.find_one({'_id':songToInsert.get('_id')})
    # verification
    assert True == actual.raw_result['updatedExisting']
    assert not None == updatedSong.get('ratings')
    if ratings == None:
     assert expectedRating == updatedSong.get('ratings')[0]
    else:
     assert expectedRating == updatedSong.get('ratings')[len(ratings)]

  def test_rate_empty_rating(self):
    """ Verify that we add a rating """
    self.verify_rate()

  def test_rate_existing_rating(self):
    """ Verify that we add a rating """
    self.verify_rate([1,2,3])

  def test_rate_should_delete_cache(self):
    self.insert_valid_test_case()
    # test
    with self.app.app_context():
      actual = self.tested.rateSong(self.song_id,5)
    # verification
    mockedCache.delete_memoized(self.tested.rating, self.tested, self.song_id)

class TestRating(TestSongServiceWithMongoMock):
  """ Get Rating """
  def test_get_average_rating_with_empty_db(self):
    """ Verify that we get an empty result from the database """
    # test
    with self.app.app_context():
      self.assertRaises(ResourceNotFoundException,
                        self.tested.rating,
                        self.song_id)

  # Unable to test the other tests cases as $avg is not implemented in mongomock
