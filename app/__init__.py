from flask import Flask
from flask_bootstrap import Bootstrap
from flask_login import LoginManager
from flask_pymongo import PyMongo

import config

login_manager = LoginManager()

mongo = PyMongo()


def create_app():
    app = Flask(__name__, instance_relative_config=True, static_folder='static')
    login_manager.init_app(app)
    login_manager.login_message = 'You must be logged in to view this page'
    login_manager.login_view = 'login'
    mongo.init_app(app)
    Bootstrap(app)
    app.config.from_object(config.DevelopmentConfig)
    app.config.from_pyfile('config.py')

    from app.auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint)

    from app.home import home as home_blueprint
    app.register_blueprint(home_blueprint)

    from app.collection import collection as collection_blueprint
    app.register_blueprint(collection_blueprint)

    from app.explore import explore as explore_blueprint
    app.register_blueprint(explore_blueprint)

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

