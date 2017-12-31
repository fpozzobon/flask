# flask API
Implementation of a simple flask API using MongoDB.

## Pre requirements
* Install and run MongoDB (ideally 3.6.0)
* Install Python (idealy Python 3)

## Quickstart
#### Use the Makefile

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

### Database manipulation :

#### Populate the database (add data and indexes)
```sh
$ flask initdb
```

> Note : the database won't be populated if there is already some documents in songs collection

#### Clean the database (empty songs collection):
```sh
$ flask cleandb
```

### Run the project :
```sh
$ python flask_api.py
```

Finally open in your browser http://127.0.0.1:5000.

### Unit Tests
#### Run the unit tests :
```sh
$ py.test tests
```
#### Run the integration-'ish' tests : (only /songs is tested)
```sh
$ python flask_integration_tests.py
```

### Possible enhancements

* [Best Practice] : use a global variable for mongodb and songService in place of app.config
* [Optimisation] : use cache on main controller
* [Marshalling] : use restfull marshaller
* [Database] : investigate a better way for dealing with _id
* [Database] : parse release date as a Date
* [Tests] : cover all the tests
* [Tests] : use patch and other handy stuff
* [Documentation] : replace the main page with a swagger documentation (using flasgger ?)
