import re, bson
from app.exceptions import SongNotFoundException, ResourceNotFoundException
from app.extensions import cache

CACHE_TIMEOUT = 500

class SongService():

  def __init__(self, songCollection, logger):
    self.songCollection = songCollection
    self.logger = logger

  def __skip_limit(self, db_find, page_size, page_num):
    skips = page_size * (page_num - 1)
    return db_find.skip(skips).limit(page_size)

  @cache.memoize(timeout=CACHE_TIMEOUT)
  def getList(self, page_size, page_num):
    self.logger.debug('Getting the songs with page size : %s and page_num : %s', page_size, page_num)
    result = self.__skip_limit(self.songCollection.find(), page_size, page_num)
    count = result.count()
    return list(result), count

  @cache.memoize(timeout=CACHE_TIMEOUT)
  def averageDifficulty(self, level=None):
    averageQuery = {'$project': {'avg': {'$avg':'$difficulty'}}}
    if level is None:
      data = list(self.songCollection.aggregate([averageQuery]))
    else:
      matchQuery = {'$match': {'level': level}}
      data = list(self.songCollection.aggregate([matchQuery,averageQuery]))
    if len(data) == 0:
      return None
    else:
      return data[0]['avg']

  def searchWithTextIndex(self, message):
    return self.songCollection.find({ "$text": { "$search": message, "$caseSensitive": False, "$diacriticSensitive": False}})

  def searchWithRegex(self, message):
    regx = re.compile(message, re.IGNORECASE)
    return self.songCollection.find({"$or": [{ "title": regx}, {"artist": regx }]})

  @cache.memoize(timeout=CACHE_TIMEOUT)
  def search(self, message):
    self.logger.debug('Searching the songs containing the message %s', message)
    # we use first the $text search as it's more efficient the drawback is that it search on the whole word
    songs = self.searchWithTextIndex(message)
    # so if we don't find anything, we do a less efficient search on the partial words
    if songs.count() == 0:
      songs = self.searchWithRegex(message)
    return list(songs)

  def find(self, song_id):
    current_song = self.songCollection.find_one({"_id": bson.ObjectId(song_id)})
    if current_song is None:
      raise SongNotFoundException(str(song_id))
    return current_song

  def rateSong(self, song_id, rating):
    self.logger.debug('Rating the song %s with %s', song_id, rating)
    cache.delete_memoized(self.rating, self, song_id)
    current_song = self.find(song_id)
    return self.songCollection.update_one(
      {"_id": current_song['_id']},
      {"$push": {
          "ratings": rating
      }})

  @cache.memoize(timeout=CACHE_TIMEOUT)
  def rating(self, song_id):
    self.logger.debug('Get the rating of the song %s', song_id)

    averageQuery = {'$project': {'avg': {'$avg':'$ratings'}}}
    matchQuery = {'$match': {'_id': bson.ObjectId(song_id)}}
    data = list(self.songCollection.aggregate([matchQuery,averageQuery]))
    if len(data) == 0:
      #Note : 404 might be not the most accurate error to give back for that case
      raise ResourceNotFoundException("no rating found for the song "+song_id)

    return data[0]['avg']
