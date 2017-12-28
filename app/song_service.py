import re, bson
from app.exceptions import SongNotFoundException, ResourceNotFoundException
from app.extensions import cache
import statistics

CACHE_TIMEOUT = 500

class SongService():

  def __init__(self, songCollection, logger):
    self.songCollection = songCollection
    self.logger = logger

  def skip_limit(self, db_find, page_size, page_num):
    skips = page_size * (page_num - 1)
    return db_find.skip(skips).limit(page_size)

  @cache.memoize(timeout=CACHE_TIMEOUT)
  def getList(self, page_size, page_num):
    self.logger.debug('Getting the songs with page size : %s and page_num : %s', page_size, page_num)
    data = self.skip_limit(self.songCollection.find(), page_size, page_num)
    count = data.count()
    return {'data':list(data), 'count':count}

  def computeAverageDifficulty(self, songs):
      if songs.count() == 0:
          return 0
      sum = 0
      for s in songs:
          sum += s['difficulty']
      return sum / songs.count()

  @cache.memoize(timeout=CACHE_TIMEOUT)
  def averageDifficulty(self, level=None):
    if level is None:
      data = self.songCollection.find()
    else:
      data = self.songCollection.find({ "level": level })
    return self.computeAverageDifficulty(data)

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
    current_song = self.find(song_id)

    ratings = current_song.get('ratings', [])
    if len(ratings) == 0:
      #Note : 404 might be not the most accurate error to give back for that case
      raise ResourceNotFoundException("no rating found for the song "+song_id)

    return statistics.mean(ratings)
