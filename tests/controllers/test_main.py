#! ../env/bin/python
# -*- coding: utf-8 -*-

import pytest
import mock
from unittest.mock import MagicMock, PropertyMock, Mock
import sys
import unittest
from flask import json, current_app

create_user = True

def createSong(id):
  return {'_id': id, 'artist': "artist" + id, 'title': "title" + id}

def createNSongs(n):
  result = []
  for i in range(n):
    result.append(createSong(str(i)))
  return result

@pytest.mark.usefixtures("app")
class TestMainSongs:
  """ Test /songs route """

  def mockSongService(self, app):
    with app.app_context():
      songService = app.config['songService'] = MagicMock()
      return songService

  def mockGetList(self, app, data, count):
    songService = self.mockSongService(app)
    songService.getList.return_value = {'data':data,'count':count}
    return songService

  def getResult(self, rv):
    return json.loads(rv.data)['result']

  def test_empty_db(self, app):
    """ Verify that we get a result from an empty database """
    # setUp
    testapp = app.test_client()
    songService = self.mockGetList(app, [], 0)

    rv = testapp.get('/songs')
    actual = self.getResult(rv)
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
    actual = self.getResult(rv)
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
