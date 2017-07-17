from flask import Flask
from flask_login import LoginManager
from flask_bootstrap import Bootstrap
from flask_pymongo import PyMongo

import config

login_manager = LoginManager()

def create_app():
    app = Flask(__name__)
    login_manager.init_app(app)
    login_manager.login_message = 'You must be logged in Nerd'
    login_manager.login_view = 'login'
    Bootstrap(app)
    app.config.from_object(config.DevelopmentConfig)
    return app

app = create_app()
mongo = PyMongo(app)

import views