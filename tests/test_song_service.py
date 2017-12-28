#! ../env/bin/python
# -*- coding: utf-8 -*-

import pytest
import unittest
from unittest.mock import MagicMock
import mongomock
from app import SongService, create_app
from tests.utils import insertNSongsInDb

mockedMongoClient=mongomock.MongoClient()

mockedSongCollection=mockedMongoClient.db.songs
mockedLogger = MagicMock()

tested = SongService(mockedSongCollection, mockedLogger)

class TestSongService(unittest.TestCase):
  """ Test Song Service """

  def setUp(self):
    self.app = create_app()
    self.app.testing = True

  def tearDown(self):
    mockedSongCollection.remove()

  def test_empty_db(self):
    """ Verify that we get an empty result from the database """
    # test
    with self.app.app_context():
      actual = tested.getList(10, 20)
    # verification
    result = list(actual['data'])
    assert [] == result
    assert 0 == actual['count']

  def test_populated_db(self):
    """ Verify that we get a result from the database """
    # result
    expectedResult=insertNSongsInDb(500, mockedSongCollection)
    # test
    with self.app.app_context():
      actual = tested.getList(10, 1)
    # verification
    result = list(actual['data'])
    assert expectedResult[0:10] == result
    assert 500 == actual['count']

  def test_populated_db_pagination(self):
    """ Verify that we get a result from the database """
    # result
    expectedResult=insertNSongsInDb(500, mockedSongCollection)
    expectedPageSize=20
    expectedPageNum=10
    # test
    with self.app.app_context():
      actual = tested.getList(expectedPageSize, expectedPageNum)
    # verification
    result = list(actual['data'])
    expectedIndex=(expectedPageSize*(expectedPageNum-1))
    assert expectedResult[expectedIndex:expectedIndex+expectedPageSize] == result
    assert 500 == actual['count']
