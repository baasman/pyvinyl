from flask import Flask
from flask_bootstrap import Bootstrap
from .decorators import setup_login_manager
from .models import db

from app.exceptions import not_found_error, server_error

from config import app_config

login_manager = setup_login_manager()

def create_app(config):

    app = Flask(__name__, instance_relative_config=True)

    login_manager.init_app(app)

    Bootstrap(app)

    app.config.from_object(app_config[config])
    app.config.from_pyfile('config.py')

    db.init_app(app)

    from app.auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint)

    from app.home import home as home_blueprint
    app.register_blueprint(home_blueprint)

    from app.collection import collection as collection_blueprint
    app.register_blueprint(collection_blueprint)

    from app.explore import explore as explore_blueprint
    app.register_blueprint(explore_blueprint)

    app.register_error_handler(500, server_error)
    app.register_error_handler(404, not_found_error)

    if not app.debug and not app.testing:
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