#! ../env/bin/python
# -*- coding: utf-8 -*-

import pytest
import unittest
from unittest.mock import MagicMock
import mongomock
from app import SongService, create_app
mockedMongoClient=mongomock.MongoClient()

mockedSongCollection=mockedMongoClient.db.songs
mockedLogger = MagicMock()

tested = SongService(mockedSongCollection, mockedLogger)

def createSong(id):
  return {'_id': id, 'artist': "artist" + id, 'title': "title" + id}

def createNSongs(n):
  result = []
  for i in range(n):
    result.append(createSong(str(i)))
  return result

def insertNSongsInDb(n):
  expectedResult = createNSongs(n)
  for song in expectedResult:
    mockedSongCollection.insert(song)
  return expectedResult

def append_songs(songs):
  output = []
  for s in songs:
    output.append({'_id': str(s['_id']), 'artist' : s['artist'], 'title' : s['title']})
  return output


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
    result = append_songs(actual['data'])
    assert [] == result
    assert 0 == actual['count']

  def test_populated_db(self):
    """ Verify that we get a result from the database """
    # result
    expectedResult=insertNSongsInDb(500)
    # test
    with self.app.app_context():
      actual = tested.getList(10, 1)
    # verification
    result = append_songs(actual['data'])
    assert expectedResult[0:10] == result
    assert 500 == actual['count']

  def test_populated_db_pagination(self):
    """ Verify that we get a result from the database """
    # result
    expectedResult=insertNSongsInDb(500)
    expectedPageSize=20
    expectedPageNum=10
    # test
    with self.app.app_context():
      actual = tested.getList(expectedPageSize, expectedPageNum)
    # verification
    result = append_songs(actual['data'])
    expectedIndex=(expectedPageSize*(expectedPageNum-1))
    assert expectedResult[expectedIndex:expectedIndex+expectedPageSize] == result
    assert 500 == actual['count']
