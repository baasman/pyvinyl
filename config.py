class Config():
    DEBUG = False
    MONGO_HOST = 'localhost'
    MONGO_PORT = 27017
    SECRET_KEY = 'comeonebruh'
    DISCOGS_USER_AGENT = 'discogs_pyvy/1.0'



class DevelopmentConfig(Config):
    DEBUG = True
    DEVELOPMENT = True


class ProductionConfig(Config):
    DEBUG = False


app_config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig
}

BREAKPOINT_VALUE = '|'

ALBUMS_PER_PAGE = 10