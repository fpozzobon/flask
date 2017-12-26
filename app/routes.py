from app import app, mongo
from flask import render_template, jsonify, request
import math

# GET /
@app.route('/')
@app.route('/about')
def home_page():
  return render_template('index.html', url_root=request.url_root)

def append_songs(songs):
  output = []
  for s in songs:
    output.append({'id': str(s['_id']), 'artist' : s['artist'], 'title' : s['title']})
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


DEFAULT_PER_PAGE = 3
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
  update_response_header(resp, result.count(), page_size, page_num)
  return resp
