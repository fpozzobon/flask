from flask import Blueprint, render_template, request
from flask_restful import Resource, Api, reqparse, abort
import math
from app.exceptions import BadRequestException
from app.view.song import append_songs
from app.song_service import songService

main = Blueprint('main', __name__)
api = Api(main)

def getSongService():
  if songService == None:
    raise Exception("app.song_service.songService null !")
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
  if count > 0:
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
    """Get songs
      ---
      parameters:
        - name: page_size
          in: query
          type: integer
          description: maximum number of songs to get
          required: false
          default: 20
        - name: page_num
          in: query
          type: integer
          description: page number to get (depending on page_size)
          required: false
          default: 1
      definitions:
        Song:
          type: object
          properties:
            _id:
              type: string
            artist:
              type: string
            title:
              type: string
            level:
              type: int
            difficulty:
              type: float
            released:
              type: string
      responses:
        200:
          description: A list of songs
          schema:
            $ref: '#/definitions/Song'
          examples:
            result: [{"artist": "The Yousicians","title": "Lycanthropic Metamorphosis","difficulty": 14.6,"level":13,"released": "2016-10-26"}]
    """
    page_size = request.args.get('page_size', DEFAULT_PER_PAGE, type=int)
    page_num = request.args.get('page_num', 1, type=int)
    data, count = getSongService().getList(page_size, page_num)
    resp = append_songs(data)
    return returnJsonResult(resp), 200, build_response_header(count,page_size,page_num)

api.add_resource(GetSongs, '/songs')

# GET /songs/avg/difficulty
class AverageDifficulty(Resource):
    def get(self, level=None):
      """Get average of difficulty
        ---
        parameters:
          - name: level
            in: path
            type: integer
            description: gives back average difficulty of all or a level
            required: false
        responses:
          200:
            description: Average of difficulty
            examples:
              result: 12.2
      """
      return returnJsonResult(getSongService().averageDifficulty(level))

api.add_resource(AverageDifficulty, '/songs/avg/difficulty', '/songs/avg/difficulty/<int:level>')

# GET /songs/search
class Search(Resource):
    def get(self):
      """Search
        ---
        parameters:
          - name: message
            in: query
            type: string
            description: message to filter on title or artist
            required: true
        responses:
          200:
            description: Returns a list of songs with the corresponding message as a title or artist
            schema:
              $ref: '#/definitions/Song'
            examples:
              result: [{"artist": "The Yousicians","title": "Lycanthropic Metamorphosis","difficulty": 14.6,"level":13,"released": "2016-10-26"}]
      """
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
    """RateSong
      ---
      parameters:
        - name: body
          in: body
          schema: {
            "required":[
              "song_id",
              "rating"
            ],
            "properties": {
              "song_id": {
                "type": "string",
                "description": "Song id to rate",
                "default":"5a4a61b691f4190c0c12740e"
              },
              "rating": {
                "type": "number",
                "description": "Rating to apply",
                "default":5
              },
            }
          }
          required: true
      responses:
        200:
          description: Returns result of adding a rate to the song
          examples:
            "result": "{'n': 1, 'nModified': 1, 'ok': 1.0, 'updatedExisting': True}"
    """
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
      """Rating
        ---
        parameters:
          - name: song_id
            in: path
            type: string
            description: song id to get the rating
            required: true
        responses:
          200:
            description: Returns the average rating of the selected song
            examples:
              result: 4
      """
      return returnJsonResult(getSongService().rating(song_id))

api.add_resource(Rating, '/songs/avg/rating/<string:song_id>')
