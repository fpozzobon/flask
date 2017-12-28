# flask API
Implementation of a simple flask API using MongoDB.

## Pre requirements
* Install and run MongoDB
* Install Python (idealy Python 3)

## Quickstart
Use the Makefile

  Or
  
### Install env :
```sh
$ easy_install pip && \
  pip install virtualenv && \
  virtualenv env && \
  . env/bin/activate && \
  make deps
```

### Install dependencies :
```sh
$ pip install -r requirements.txt
```

### Setup the environment variables :
```sh
$ export FLASK_APP=flask_initdb.py
$ export FLASK_API_DB_URL=mongodb://localhost:27017/<yourcollection>>
```

> Note : databaseUrl is optional, if not used the application will connect to mongodb://localhost:27017/flask

### Populate the database :
```sh
$ flask initdb
```

> Note : the database won't be populated if there is already some documents in songs collection

Clean the database (empty songs collection):
```sh
$ flask cleandb
```

Run the project :
```sh
$ python flask_api.py
```

Finally open in your browser http://127.0.0.1:5000.

### Unit Tests
Run the unit tests :
```sh
$ py.test tests
```
Run the integration-'ish' tests : (only /songs is tested)
```sh
$ python flask_integration_tests.py
```

### Possible enhancements

* [Optimisation] : use $avg on mongodb query
* [Marshalling] : use restfull marshaller
* [Marshalling] : return the other properties from songs
* [Database] : parse release date as a Date
* [Tests] : cover all the tests
