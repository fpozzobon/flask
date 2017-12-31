from flask import current_app, Blueprint, render_template, jsonify, request
from flask_restful import Resource, Api, reqparse, abort, fields, marshal_with
import math
from app.exceptions import BadRequestException
from app.view.song import formatSong, append_songs

main = Blueprint('main', __name__)
api = Api(main)

def getSongService():
  songService = current_app.config.get('songService')
  if songService == None:
    raise Exception("SongService missing from current_app.config['songService'] !")
  return songService

@main.route('/')
@main.route('/about')
def home_page():
  return render_template('index.html', url_root=request.url_root)

# Default json result
# Note : consumers may prefer not having that 'result' wrap around the result
def returnJsonResult(result):
  return {'result' : result}

def build_link(page_size, page_num, rel):
  return "<%(url)s?page_size=%(size)d&page_num=%(num)d>; rel='%(rel)s'" % {'url':request.base_url, 'size':page_size, 'num':page_num, 'rel':rel}

# Update the response header table with X-total-count and Link
# depending on count / page_size / page_num
def build_response_header(count, page_size, page_num):
  # links next / last / first / prev
  links = []
  if (page_size * page_num) < count:
    links.append(build_link(page_size, page_num + 1, 'next'))
  if page_size > 0:
    links.append(build_link(page_size, math.ceil(count / page_size), 'last'))
  links.append(build_link(page_size, 1, 'first'))
  if page_num > 1:
    links.append(build_link(page_size, page_num - 1, 'prev'))

  return {'X-total-count': count, 'Link': ', '.join(links)}

DEFAULT_PER_PAGE = 20
# GET /songs
class GetSongs(Resource):

  def get(self):
    page_size = request.args.get('page_size', DEFAULT_PER_PAGE, type=int)
    page_num = request.args.get('page_num', 1, type=int)
    data, count = getSongService().getList(page_size, page_num)
    resp = append_songs(data)
    return returnJsonResult(resp), 200, build_response_header(count,page_size,page_num)

api.add_resource(GetSongs, '/songs')

# GET /songs/avg/difficulty
class AverageDifficulty(Resource):
    def get(self, level=None):
      return returnJsonResult(getSongService().averageDifficulty(level))

api.add_resource(AverageDifficulty, '/songs/avg/difficulty', '/songs/avg/difficulty/<int:level>')

# GET /songs/search
class Search(Resource):
    def get(self):
      message = request.args.get('message')
      if message == None:
        abort(400, message="'message' parameter is missing ! Please provide one. Example : /songs/search?message=you")

      return returnJsonResult(append_songs(getSongService().search(message)))

api.add_resource(Search, '/songs/search')

# POST /songs/rating
# Note : we may want to apply a limitation on the precision for rating in the future
# TODO validate if we want to add a timestamp to each rating
class RateSong(Resource):

  def __init__(self):
    self.parser = reqparse.RequestParser()
    self.parser.add_argument('song_id',
        help="Missing 'song_id' property !",
        required=True)
    self.parser.add_argument('rating',
                             type=float,
                             help="Missing 'rating' property to apply to the song !",
                             required=True)

  def post(self):
    args= self.parser.parse_args(strict=True)
    rating = args['rating']
    song_id = args['song_id']

    # rating should be between 1 and 5
    if rating < 1 or rating > 5:
      raise BadRequestException("Rating should be between 1 and 5")

    update_result = getSongService().rateSong(song_id, rating)

    if not update_result.raw_result['updatedExisting']:
      return "Error when updating %(id)s, %(msg)s" % {'id': str(song_id), 'msg':update_result.raw_result}, 500
    return returnJsonResult(str(update_result.raw_result))

api.add_resource(RateSong, '/songs/rating')


# GET /songs/avg/rating/<string:song_id>
class Rating(Resource):
    def get(self,song_id):
      return returnJsonResult(getSongService().rating(song_id))

api.add_resource(Rating, '/songs/avg/rating/<string:song_id>')
