# flask API
Implementation of a simple flask API using MongoDB.

## Dependencies
Install and run MongoDB
Install Python (idealy python 3)

## Quickstart
Install Flask-PyMongo :
  pip install Flask-PyMongo

Setup the environment variables :
  export FLASK_APP=flask_api

  export FLASK_API_DB_URL=mongodb://localhost:27017/<yourcollection>>
  Note : databaseUrl is optional, if not used the application will connect to mongodb://localhost:27017/flask

Populate the database :
  flask initdb <databaseUrl>
Note : the database won't be populated if there is already some documents in songs collection

Run the project :
  python flask_api.py or flask run

Finally open in your browser http://127.0.0.1:5000.

## Unit Tests
Install mongomock :
    pip install mongomock
Run the tests :
    python flask_api_tests.py
