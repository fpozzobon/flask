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

def insertNSongsInDb(n):
  expectedResult = createNSongs(n)
  for song in expectedResult:
    mockedMongoClient.db.songs.insert(song)
  return expectedResult

class getSongsTestCases(unittest.TestCase):

  def setUp(self):
    flask_api.app.testing = True
    self.app = flask_api.app.test_client()

  def tearDown(self):
    mockedMongoClient.db.songs.remove()

  def getResult(self, rv):
    return json.loads(rv.data)['result']

  # Verify that we get a result from an empty database
  def test_empty_db(self):
    rv = self.app.get('/songs')
    actual = self.getResult(rv)
    self.assertEqual(0, len(actual))
    self.assertEqual([], actual)

  # Verify that we get a result from an empty database even with a pagination
  def test_empty_db_with_pagination_arguments(self):
    rv = self.app.get('/songs?page_num=5&page_size=30')
    actual = self.getResult(rv)
    self.assertEqual(0, len(actual))
    self.assertEqual([], actual)

  # Verify that we get a result on page 1
  def test_db_not_empty(self):
    expectedPageSize = 15
    expectedResult = insertNSongsInDb(30)

    rv = self.app.get('/songs?page_size=' + str(expectedPageSize))
    actual = self.getResult(rv)
    self.assertEqual(expectedPageSize, len(actual))
    for i in range(expectedPageSize):
      self.assertEqual(expectedResult[i], actual[i])

  # Verify that we get a result on page 5 with a size of 3
  def test_db_not_empty_with_pagination(self):
    expectedPageSize = 3
    expectedPageNum = 5
    expectedSkip=expectedPageSize*(expectedPageNum-1)
    expectedResult = insertNSongsInDb(50)

    rv = self.app.get('/songs?page_num='+str(expectedPageNum)+'&page_size=' + str(expectedPageSize))
    actual = self.getResult(rv)
    self.assertEqual(expectedPageSize, len(actual))
    for i in range(expectedPageSize):
      self.assertEqual(expectedResult[i+expectedSkip], actual[i])

  # Verify that count applies to all elements in the database
  def test_count_header(self):
    # Setup
    expectedCount = 50
    expectedResult = insertNSongsInDb(expectedCount)
    # Test
    rv = self.app.get('/songs?page_num=2&page_size=5')
    # Verification
    self.assertEqual(str(expectedCount), rv.headers['X-total-count'], rv.headers);

  #TODO add unit test for headers

if __name__ == '__main__':
  unittest.main()
