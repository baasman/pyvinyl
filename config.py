import os

class Config():
    DEBUG = False

    MONGO_HOST = 'ds151163.mlab.com'
    MONGO_PORT = 51163
    MONGO_USERNAME = 'baasman'
    MONGO_DBNAME = 'app'

    MONGO2_DBNAME = 'test'

    SECRET_KEY = 'somethingsecret'
    DISCOGS_USER_AGENT = 'discogs_pyvy/1.0'


class DevelopmentConfig(Config):
    DEBUG = True
    DEVELOPMENT = True


class TestingConfig(Config):

    MONGO2_HOST = 'localhost'
    MONGO2_PORT = 27017

    TESTING = True
    DEBUG = False
    CSRF_ENABLED = False
    PRESERVE_CONTEXT_ON_EXCEPTION = False


class ProductionConfig(Config):
    DEBUG = False


app_config = {
    'testing': TestingConfig,
    'development': DevelopmentConfig,
    'production': ProductionConfig
}

BREAKPOINT_VALUE = '|'

ALBUMS_PER_PAGE = 10