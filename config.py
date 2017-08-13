class Config():
    DEBUG = False
    MONGO_HOST = 'localhost'
    MONGO_PORT = 27017
    MONGO2_DBNAME = 'test'
    SECRET_KEY = 'comeonebruh'
    DISCOGS_USER_AGENT = 'discogs_pyvy/1.0'


class DevelopmentConfig(Config):
    DEBUG = True
    DEVELOPMENT = True


class TestingConfig(Config):
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