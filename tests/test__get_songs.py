import mock
from unittest.mock import MagicMock, PropertyMock, Mock
import sys
import mongomock
mockedMongo = MagicMock()
mockedMongoClient = mongomock.MongoClient()
mockedMongo.PyMongo.return_value = mockedMongoClient
sys.modules['flask_pymongo'] = mockedMongo
import unittest
from flask import json

import flask_api

def createSong(id):
  return {'_id': id, 'artist': "artist" + id, 'title': "title" + id}

def createNSongs(n):
  result = []
  for i in range(n):
    result.append(createSong(str(i)))
  return result

class flaskApiTestCase(unittest.TestCase):

  def setUp(self):
    flask_api.app.testing = True
    self.app = flask_api.app.test_client()

  def tearDown(self):
    mockedMongoClient.db.songs.remove()

  def test_empty_db(self):
    rv = self.app.get('/songs')
    self.assertEqual([], json.loads(rv.data)['result'])

  def test_empty_db_with_pagination_arguments(self):
    rv = self.app.get('/songs?page_num=5&page_size=30')
    self.assertEqual([], json.loads(rv.data)['result'])

  def test_db_not_empty(self):
    expectedPageSize = 15
    expectedResult = createNSongs(30)
    for song in expectedResult:
      mockedMongoClient.db.songs.insert(song)

    rv = self.app.get('/songs?page_num=1&page_size=' + str(expectedPageSize))
    actual = json.loads(rv.data)['result']
    self.assertEqual(expectedPageSize, len(actual))
    for i in range(expectedPageSize):
      self.assertEqual(expectedResult[i], actual[i])

  def test_db_not_empty_with_pagination(self):
    expectedPageSize = 3
    expectedPageNum = 5
    expectedSkip=expectedPageSize*(expectedPageNum-1)
    expectedResult = createNSongs(50)
    for song in expectedResult:
      mockedMongoClient.db.songs.insert(song)

    rv = self.app.get('/songs?page_num='+str(expectedPageNum)+'&page_size=' + str(expectedPageSize))
    actual = json.loads(rv.data)['result']
    self.assertEqual(expectedPageSize, len(actual))
    for i in range(expectedPageSize):
      self.assertEqual(expectedResult[i+expectedSkip], actual[i])
