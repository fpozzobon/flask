from flask import Blueprint, request
from flask_restful import Resource, Api, reqparse, abort, fields, marshal_with
import math
from app.song_service import songService

main = Blueprint('main', __name__)
api = Api(main, '/songs')

envelope = 'result'
song_fields = {
    '_id': fields.String,
    'artist': fields.String,
    'title': fields.String,
    'level': fields.String,
    'difficulty': fields.String,
    'released': fields.String
}

avg_fields = {
    envelope: fields.Float
}

update_fields = {
    'n': fields.Integer,
    'nModified': fields.Integer,
    'ok': fields.Float,
    'updatedExisting': fields.Boolean
}


def getSongService():
    if songService is None:
        raise Exception("app.song_service.songService null !")
    return songService


def build_link(page_size, page_num, rel):
    return "<%(url)s?page_size=%(size)d&page_num=%(num)d>; rel='%(rel)s'" % {'url': request.base_url,
                                                                             'size': page_size,
                                                                             'num': page_num,
                                                                             'rel': rel}


# Update the response header table with X-total-count and Link
# depending on count / page_size / page_num
def build_response_header(count, page_size, page_num):
    # links next / last / first / prev
    links = []
    if count > 0:
        if (page_size * page_num) < count:
            links.append(build_link(page_size, page_num + 1, 'next'))
        if page_size > 0:
            links.append(build_link(page_size,
                                    math.ceil(count / page_size),
                                    'last'))
        links.append(build_link(page_size, 1, 'first'))
        if page_num > 1:
            links.append(build_link(page_size, page_num - 1, 'prev'))

    return {'X-total-count': count, 'Link': ', '.join(links)}


DEFAULT_PER_PAGE = 20


# GET /songs
class GetSongs(Resource):

    def __init__(self):
        self.parser = reqparse.RequestParser()
        self.parser.add_argument('page_size',
                                 required=False,
                                 type=int,
                                 default=DEFAULT_PER_PAGE)
        self.parser.add_argument('page_num',
                                 required=False,
                                 type=int,
                                 default=1)

    @marshal_with(song_fields, envelope=envelope)
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
                        result: [{"artist": "The Yousicians",
                                  "title": "Lycanthropic Metamorphosis",
                                  "difficulty": 14.6,"level":13,
                                  "released":"2016-10-26"}]
        """
        args = self.parser.parse_args(strict=True)
        page_size = args.get('page_size')
        page_num = args.get('page_num')
        data, count = getSongService().getList(page_size, page_num)
        return data, 200, build_response_header(count,
                                                page_size,
                                                page_num)


api.add_resource(GetSongs, '/')


# GET /songs/avg/difficulty
class AverageDifficulty(Resource):

    @marshal_with(avg_fields)
    def get(self, level=None):
        """Get average of difficulty
            ---
            parameters:
                - name: level
                  in: path
                  type: integer
                  description: gives back average difficulty of all or a level
                  required: false
            definitions:
                Average:
                  type: float
            responses:
              200:
                description: Average of difficulty
                schema:
                  $ref: '#/definitions/Average'
                examples:
                  result: 12.2
        """
        return {envelope: getSongService().averageDifficulty(level)}


api.add_resource(AverageDifficulty,
                 '/avg/difficulty',
                 '/avg/difficulty/<int:level>')


# GET /songs/search
class Search(Resource):

    def __init__(self):
        self.parser = reqparse.RequestParser()
        self.parser.add_argument('message',
                                 help="Missing 'message' argument !",
                                 required=True)

    @marshal_with(song_fields, envelope=envelope)
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
                description: Returns a list of songs with
                    the corresponding message as a title or artist
                schema:
                  $ref: '#/definitions/Song'
                examples:
                  result: [{"artist": "The Yousicians",
                            "title": "Lycanthropic Metamorphosis",
                            "difficulty": 14.6,
                            "level":13,
                            "released": "2016-10-26"}]
        """
        args = self.parser.parse_args(strict=True)
        message = args['message']
        if message is None:
            abort(400, message="'message' parameter is missing ! "
                  "Please provide one. Example : /songs/search?message=you")

        return getSongService().search(message)


api.add_resource(Search, '/search')


# POST /songs/rating
# Note : we may want to apply a limitation
# on the precision for rating in the future
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

    @marshal_with(update_fields)
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
            definitions:
                UpdateResult:
                  type: object
                  properties:
                    n:
                      type: int
                    nModified:
                      type: int
                    ok:
                      type: float
                    updatedExisting:
                      type: boolean
            responses:
                200:
                    description: Returns result of adding a rate to the song
                    schema:
                      $ref: '#/definitions/UpdateResult'
                    examples:
                        "result": "{'n': 1, 'nModified': 1, 'ok': 1.0, 'updatedExisting': True}"
        """
        args = self.parser.parse_args(strict=True)
        rating = args['rating']
        song_id = args['song_id']

        update_result = getSongService().rateSong(song_id, rating)

        if not update_result.raw_result['updatedExisting']:
            return "Error when updating %(id)s, %(msg)s" % {'id': str(song_id),
                                                            'msg': update_result.raw_result},
            500
        return update_result.raw_result


api.add_resource(RateSong, '/rating')


# GET /songs/avg/rating/<string:song_id>
class Rating(Resource):
    @marshal_with(avg_fields)
    def get(self, song_id):
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
                    schema:
                      $ref: '#/definitions/Average'
                    examples:
                        result: 4
        """
        return {envelope: getSongService().rating(song_id)}


api.add_resource(Rating, '/avg/rating/<string:song_id>')
