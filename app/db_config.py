import os
from flask_pymongo import PyMongo

DEFAULT_DATABASE_URL = 'mongodb://localhost:27017/flask'


def configureDatabase(app):
    app.config['MONGO_URI'] = os.environ.get('FLASK_API_DB_URL',
                                             DEFAULT_DATABASE_URL)
    app.logger.info('Connecting to the database : %s', app.config['MONGO_URI'])

    mongo = PyMongo(app)

    @app.teardown_appcontext
    def teardown_db(exception):
        if mongo.cx is not None:
            mongo.cx.close()

    return mongo
