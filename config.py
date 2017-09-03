import os

class Config():
    DEBUG = False

    MONGODB_HOST = 'mongodb://ds151163.mlab.com:51163/app'
    MONGODB_DB = 'app'

    DISCOGS_USER_AGENT = 'discogs_pyvy/1.0'


class DevelopmentConfig(Config):
    DEBUG = True
    DEVELOPMENT = True

    MONGODB_HOST = 'localhost'
    MONGODB_PORT = 27017
    MONGODB_DB = 'dev'


class TestingConfig(Config):
    TESTING = True
    DEBUG = False
    CSRF_ENABLED = False
    PRESERVE_CONTEXT_ON_EXCEPTION = False

    MONGODB_HOST = 'localhost'
    MONGODB_PORT = 27017
    MONGODB_DB = 'test'


class ProductionConfig(Config):
    DEBUG = False



app_config = {
    'testing': TestingConfig,
    'development': DevelopmentConfig,
    'production': ProductionConfig
}

BREAKPOINT_VALUE = '|'

ALBUMS_PER_PAGE = 10