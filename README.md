# Resturant APP

##Installing steps
1. Untar the tar file using
    tar -xvf restaurant_review.tar
2. Change directory to cd resturant_review
    cd restaurant_review
3. Make sure you are using Python2.7 and virtualenv is installed
    a. Ubuntu or linux
        pip install virtualenv
    b. Mac users only
        brew install virtualenv
4. Sourcing the env.sh file
    source tools/env.sh

## Running the app
1. Initialize the db by running this command
    python -m revapp.manage db upgrade
2. Running the app
    python server.py

## Schemas are upgradable and downgradable using Alembic versioning
1. To create a migration repository
    python -m revapp.manage db init
2. To initialize migration
    python -m revapp.manage db migrate
3. If the user has uploaded migration script. After reviewing please run the following
    command to migrate to new version
    python -m revapp.manage db upgrade

# Dropping using database
1. Use the following command to drop the
    python -m revapp.manage drop

# Create using database
1. Use the following command to create the db
    python -m revapp.manage create

# Making Schema changes or Adding new Schema.
1. If you are planning to make some schema changes. Make sure you run the command and upload
    the revision_.py
    python -m revapp.manage db migrate

# Debug URL map
1. Use the following command to see url_map
    python -m revapp.manage list_routes

## Debugging the flask
Execute Python in bash with virtualenv enabled
python
```
>>> from flask import Flask
>>> from flask_sqlalchemy import SQLAlchemy
>>> app.config.from_object(settings)
>>> db = SQLAlchemy(app)
>>> app_ctx = app.app_context()
>>> app_ctx.push()
>>> app.name
'revapp'
>>> app.url_map
Map([<Rule '/user' (HEAD, POST, OPTIONS, GET) -> user>,
<Rule '/' (HEAD, OPTIONS, GET) -> hello_world>,
<Rule '/static/<filename>' (HEAD, OPTIONS, GET) -> static>])
```