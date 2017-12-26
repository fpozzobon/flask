from app import app, mongo
from flask import render_template, jsonify, request
import math
import re, bson
import statistics

# GET /
@app.route('/')
@app.route('/about')
def home_page():
  return render_template('index.html', url_root=request.url_root)

def append_songs(songs):
  output = []
  for s in songs:
    output.append({'_id': str(s['_id']), 'artist' : s['artist'], 'title' : s['title']})
  return output

def skip_limit(db_find, page_size, page_num):
  skips = page_size * (page_num - 1)
  return db_find.skip(skips).limit(page_size)

def build_link(page_size, page_num, rel):
  return "<"+request.base_url+"?page_size="+str(page_size)+"&page_num="+str(page_num)+">; rel='"+rel+"'"

# Update the response header table with X-total-count and Link
# depending on count / page_size / page_num
def update_response_header(response, count, page_size, page_num):
  # count header
  response.headers['X-total-count'] = count

  app.logger.info('Getting the songs with page size : %s', request)

  # links next / last / first / prev
  links = []
  if (page_size * page_num) < count:
    links.append(build_link(page_size, page_num + 1, 'next'))
  if page_size > 0:
    links.append(build_link(page_size, math.ceil(count / page_size), 'last'))
  links.append(build_link(page_size, 1, 'first'))
  if page_num > 1:
    links.append(build_link(page_size, page_num - 1, 'prev'))

  response.headers['Link'] = ', '.join(links)


DEFAULT_PER_PAGE = 20
# GET /songs
@app.route('/songs')
def songs():
  song = mongo.db.songs
  page_size = request.args.get('page_size', DEFAULT_PER_PAGE, type=int)
  page_num = request.args.get('page_num', 1, type=int)
  app.logger.info('Getting the songs with page size : %s and page_num : %s', page_size, page_num)
  result = skip_limit(song.find(), page_size, page_num)
  appended_songs = append_songs(result)
  resp = jsonify({'result' : appended_songs})
  update_response_header(resp, song.count(), page_size, page_num)
  return resp

# GET /songs/avg/difficulty
@app.route('/songs/avg/difficulty')
@app.route('/songs/avg/difficulty/<int:level>')
def average_difficulty(level=None):
  song = mongo.db.songs
  if level is None:
      average = computeAverageDifficulty(song.find())
  else:
      average = computeAverageDifficulty(song.find({ "level": level }))
  return jsonify({'result' : average})

def computeAverageDifficulty(songs):
    if songs.count() == 0:
        return 0
    sum = 0
    for s in songs:
        sum += s['difficulty']
    return sum / songs.count()

# GET /songs/search
@app.route('/songs/search')
def search():
  message = request.args.get('message')
  app.logger.info('Search the songs containing the message %s', message)
  if message == None:
    return jsonify({'result' : "Error, message argument missing!"})
  song = mongo.db.songs
  regx = re.compile(message, re.IGNORECASE)
  songs = song.find({"$or": [{ "title": regx}, {"artist": regx }]})
  return jsonify({'result' : append_songs(songs)})

# POST /songs/rating
# Note : we may want to apply a limitation on the precision for rating in the future
# TODO validate if we want to add a timestamp to each rating
@app.route('/songs/rating', methods=['POST'])
def rate_song():
  song = mongo.db.songs
  song_id = bson.ObjectId(request.json['song_id'])
  rating = request.json['rating']

  app.logger.info('Rating the song %s with %s', song_id, rating)

  # rating should be between 1 and 5
  # TODO replace that with a proper error response
  if rating < 1 or rating > 5:
      return jsonify({'result' : "Error rating should be between 1 and 5 !"})

  current_song = song.find_one({"_id": song_id})
  if current_song is None:
    return jsonify({'result' : "Error no song found for id "+song_id+"!"})

  update_result = song.update_one(
    {"_id": song_id},
    {"$push": {
        "ratings": rating
    }})

  return jsonify({'result' : str(update_result.raw_result)})

# GET /songs/avg/rating/<string:song_id>
@app.route('/songs/avg/rating/')
@app.route('/songs/avg/rating/<string:song_id>')
def rating(song_id):
  song = mongo.db.songs

  app.logger.info('Get the rating of the song %s', song_id)

  current_song = song.find_one({"_id": bson.ObjectId(song_id)})
  if current_song is None:
    return jsonify({'result' : "Error no song found for this id "+song_id+" !"})

  ratings = current_song.get('ratings', [])
  if len(ratings) == 0:
    return jsonify({'result' : "No rating for that song at the moment !"})
  return jsonify({'result' : statistics.mean(ratings)})
