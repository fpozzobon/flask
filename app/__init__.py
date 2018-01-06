from flask import Flask, render_template, request
from app.controllers.main import main
from app.db_config import configureDatabase
from app.exceptions import ResourceNotFoundException, BadRequestException
from app.extensions import cache
from app.song_service import songService
from flasgger import Swagger


def create_app():
    app = Flask(__name__)

    # initialize the cache
    cache.init_app(app,
                   config={'CACHE_TYPE': 'simple'})

    with app.app_context():
        cache.clear()

    # Error handling
    @app.errorhandler(ResourceNotFoundException)
    def resource_not_found(e):
        return "Resource not found : %s" % str(e), 404

    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('404.html', url_root=request.url_root), 404

    @app.errorhandler(BadRequestException)
    def handle_bad_request(e):
        return "Bad request : %s" % str(e), 400

    apiPrefix = 'api/v1'

    @app.route('/')
    @app.route('/about')
    def home_page():
        return render_template('index.html', url_root=request.url_root + apiPrefix + '/')

    # Database connection and main route connection
    with app.app_context():
        mongo = configureDatabase(app)
        songService.init(mongo.db.songs, app.logger)

    # register our blueprints
    app.register_blueprint(main, url_prefix='/' + apiPrefix)

    app.config['SWAGGER'] = {
        'title': 'Flask API - Training',
        'version': 1,
        'description': 'A simple training on Flask'
    }

    Swagger(app)

    return app
