# flask API
Implementation of a simple flask API using MongoDB.

## Pre requirements
Install and run MongoDB
Install Python (idealy Python 3)

## Quickstart
Use the Makefile

  Or

Install env :
  easy_install pip && \
  pip install virtualenv && \
  virtualenv env && \
  . env/bin/activate && \
  make deps

Install dependencies :
  pip install -r requirements.txt

Setup the environment variables :
  export FLASK_APP=flask_initdb.py
  export FLASK_API_DB_URL=mongodb://localhost:27017/<yourcollection>>

  Note : databaseUrl is optional, if not used the application will connect to mongodb://localhost:27017/flask

Populate the database :
  flask initdb

  Note : the database won't be populated if there is already some documents in songs collection

Clean the database (empty songs collection):
  flask cleandb

Run the project :
  python flask_api.py

Finally open in your browser http://127.0.0.1:5000.

## Unit Tests
Run the unit tests :
    py.test tests
Run the integration-'ish' tests : (only /songs is tested)
    python flask_integration_tests.py
