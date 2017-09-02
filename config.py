import os

class Config():
    DEBUG = False

    MONGO_HOST = 'ds151163.mlab.com'
    MONGO_PORT = 51163
    MONGO_DBNAME = 'app'

    DISCOGS_USER_AGENT = 'discogs_pyvy/1.0'


class DevelopmentConfig(Config):
    DEBUG = True
    DEVELOPMENT = True

    MONGO_HOST = 'localhost'
    MONGO_PORT = 27017
    MONGO_DBNAME = 'test'


class TestingConfig(Config):
    TESTING = True
    DEBUG = False
    CSRF_ENABLED = False
    PRESERVE_CONTEXT_ON_EXCEPTION = False

    MONGO_HOST = 'localhost'
    MONGO_PORT = 27017
    MONGO_DBNAME = 'test'


class ProductionConfig(Config):
    DEBUG = False


app_config = {
    'testing': TestingConfig,
    'development': DevelopmentConfig,
    'production': ProductionConfig
}

BREAKPOINT_VALUE = '|'

ALBUMS_PER_PAGE = 10