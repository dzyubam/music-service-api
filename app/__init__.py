from flask import Flask
from flask_restful import reqparse, abort, Api, Resource

# Initialize the app
app = Flask(__name__, instance_relative_config=True)
app.secret_key = 'kja;sf;kj;aksdf()*&908)(*)'

# Load the views
from app import api_v1

# Load the config file
app.config.from_object('config')

# Load DB
from app.database import init_db

init_db()
