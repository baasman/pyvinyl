class Config():
    DEBUG = False
    MONGO_HOST = 'localhost'
    MONGO_PORT = 27017
    SECRET_KEY = 'comeonebruh'



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