from flask import Flask
from flask_login import LoginManager
from flask_bootstrap import Bootstrap
from flask_pymongo import PyMongo

import discogs_client
import pylast

import config

login_manager = LoginManager()

def create_app():
    app = Flask(__name__, instance_relative_config=True, static_folder='static')
    login_manager.init_app(app)
    login_manager.login_message = 'You must be logged in Nerd'
    login_manager.login_view = 'login'
    Bootstrap(app)
    app.config.from_object(config.DevelopmentConfig)
    app.config.from_pyfile('config.py')

    if not app.debug:
        import logging
        from logging.handlers import RotatingFileHandler
        file_handler = RotatingFileHandler('tmp/record_recorder.log', 'a',
                                           1 * 1024 * 1024, 10)
        file_handler.setLevel(logging.INFO)
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'))
        app.logger.addHandler(file_handler)
        app.logger.setLevel(logging.INFO)
        app.logger.info('Record record startup')

    return app

app = create_app()
mongo = PyMongo(app)

user_agent = 'discogs_pyvy/1.0'
dclient = discogs_client.Client(user_agent)
dclient.set_consumer_key(app.config['DISCOGS_CONSUMER_KEY'], app.config['DISCOGS_CONSUMER_SECRET'])
dclient.set_token(app.config['ACCESS_TOKEN'], app.config['ACCESS_SECRET'])

lastfm_client = pylast.LastFMNetwork(api_key=app.config['LASTFM_API_KEY'],
                                     api_secret=app.config['LASTFM_API_SECRET'])

import views