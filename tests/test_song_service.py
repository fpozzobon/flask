#! ../env/bin/python
# -*- coding: utf-8 -*-

import pytest
from app.exceptions import SongNotFoundException, ResourceNotFoundException
from tests.utils import insertNSongsInDb
import bson

song_id = "5a44f39191f4196576cb1eb2"


@pytest.mark.usefixtures("song_service")
class TestGetList():
    """ Get List """
    def test_get_list_with_empty_db(self, song_service):
        """ Verify that we get an empty result from the database """
        # test
        tested, mockedSongCollection, mockedCache = song_service
        data, count = tested.getList(10, 20)
        # verification
        assert [] == data
        assert 0 == count

    def test_get_list_with_populated_db(self, song_service):
        """ Verify that we get a result from the database """
        # result
        tested, mockedSongCollection, mockedCache = song_service
        expectedResult = insertNSongsInDb(500, mockedSongCollection)
        # test
        data, count = tested.getList(10, 1)
        # verification
        assert expectedResult[0:10] == data
        assert 500 == count

    def test_get_list_with_populated_db_pagination(self, song_service):
        """ Verify that we get a result from the database """
        # result
        tested, mockedSongCollection, mockedCache = song_service
        expectedCount = 500
        expectedPageSize = 20
        expectedPageNum = 10
        expectedResult = insertNSongsInDb(expectedCount, mockedSongCollection)
        # test
        data, count = tested.getList(expectedPageSize, expectedPageNum)
        # verification
        expectedIndex = (expectedPageSize * (expectedPageNum - 1))
        assert expectedResult[expectedIndex: (expectedIndex + expectedPageSize)] == data
        assert expectedCount == count


@pytest.mark.usefixtures("song_service")
class TestAverageDifficulty:
    """ Get AverageDifficulty """
    def test_get_average_difficulty_with_empty_db(self, song_service):
        """ Verify that we get an empty result from the database """
        # test
        tested, mockedSongCollection, mockedCache = song_service
        actual = tested.averageDifficulty()
        # verification
        assert 0 == actual

    def __insertSongWithDifficulty(self, mockedSongCollection, difficulty, level):
        mockedSongCollection.insert({'difficulty': difficulty,
                                     'level': level})

    def test_get_average_difficulty(self, song_service):
        """ Verify that we get a result from the database """
        # result
        tested, mockedSongCollection, mockedCache = song_service
        self.__insertSongWithDifficulty(mockedSongCollection, 10, 10)
        self.__insertSongWithDifficulty(mockedSongCollection, 5, 15)
        self.__insertSongWithDifficulty(mockedSongCollection, 3, 11)
        # test
        actual = tested.averageDifficulty()
        # verification
        assert 6 == actual

    def test_get_average_difficulty_on_level(self, song_service):
        """ Verify that we get a result for a specific level from the database """
        # result
        tested, mockedSongCollection, mockedCache = song_service
        self.__insertSongWithDifficulty(mockedSongCollection, 10, 10)
        self.__insertSongWithDifficulty(mockedSongCollection, 5, 10)
        self.__insertSongWithDifficulty(mockedSongCollection, 3, 11)
        # test
        actual = tested.averageDifficulty(10)
        # verification
        assert 7.5 == actual


@pytest.mark.usefixtures("song_service")
class TestSearch:
    """ Search """
    def test_search_with_empty_db(self, song_service):
        """ Verify that we get an empty result from the database """
        # test
        tested, mockedSongCollection, mockedCache = song_service
        actual = tested.search("anymessage")
        # verification
        assert [] == actual

    def test_search_on_title(self, song_service):
        """ Verify that we get a result from the database """
        # result
        tested, mockedSongCollection, mockedCache = song_service
        expectedResult = insertNSongsInDb(5, mockedSongCollection)
        # test
        actual = tested.search("title1")
        # verification
        assert [expectedResult[1]] == actual

    def test_search_on_artist(self, song_service):
        """ Verify that we get a result from the database """
        # result
        tested, mockedSongCollection, mockedCache = song_service
        expectedResult = insertNSongsInDb(10, mockedSongCollection)
        # test
        actual = tested.search("artist5")
        # verification
        assert [expectedResult[5]] == actual

    def test_search_on_partial_word(self, song_service):
        """ Verify that we get a result from the database """
        # result
        tested, mockedSongCollection, mockedCache = song_service
        expectedResult = insertNSongsInDb(10, mockedSongCollection)
        # test
        actual = tested.search("art")
        # verification
        assert expectedResult == actual


@pytest.mark.usefixtures("song_service")
class TestRateSong:
    """ Rate Song """
    def test_rate_with_empty_db(self, song_service):
        """ Verify that we get an exception SongNotFoundException """
        # test
        tested, mockedSongCollection, mockedCache = song_service
        with pytest.raises(SongNotFoundException):
            tested.rateSong(song_id, 123)

    def __insert_valid_test_case(self, mockedSongCollection, ratings=None):
        # setup
        songToInsert = {'_id': bson.ObjectId(song_id)}
        if ratings is not None:
            songToInsert['ratings'] = ratings
        mockedSongCollection.insert(songToInsert)
        return songToInsert

    def __verify_rate(self, tested, mockedSongCollection, ratings=None):
        # setup
        expectedRating = 123.3
        songToInsert = self.__insert_valid_test_case(mockedSongCollection, ratings)
        # test
        actual = tested.rateSong(song_id, expectedRating)
        updatedSong = mockedSongCollection.find_one({'_id': songToInsert.get('_id')})
        # verification
        assert actual.raw_result['updatedExisting'] is True
        assert updatedSong.get('ratings') is not None
        if ratings is None:
            assert expectedRating == updatedSong.get('ratings')[0]
        else:
            assert expectedRating == updatedSong.get('ratings')[len(ratings)]

    def test_rate_empty_rating(self, song_service):
        """ Verify that we add a rating """
        tested, mockedSongCollection, mockedCache = song_service
        self.__verify_rate(tested, mockedSongCollection)

    def test_rate_existing_rating(self, song_service):
        """ Verify that we add a rating """
        tested, mockedSongCollection, mockedCache = song_service
        self.__verify_rate(tested, mockedSongCollection, [1, 2, 3])

    def test_rate_should_delete_cache(self, song_service):
        tested, mockedSongCollection, mockedCache = song_service
        self.__insert_valid_test_case(mockedSongCollection)
        # test
        tested.rateSong(song_id, 5)
        # verification
        mockedCache.delete_memoized.assert_called_with(tested.rating, tested, song_id)


@pytest.mark.usefixtures("song_service")
class TestRating:
    """ Get Rating """
    def test_get_average_rating_with_empty_db(self, song_service):
        """ Verify that we get an empty result from the database """
        # test
        tested, mockedSongCollection, mockedCache = song_service
        with pytest.raises(ResourceNotFoundException):
            tested.rating(song_id)

    # Unable to test the other tests cases as $avg is not implemented in mongomock
