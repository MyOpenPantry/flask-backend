class Config(object):
    SQLALCHEMY_DATABASE_URI = 'sqlite:///pantry.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    DEBUG = False
    TESTING = False

class ProductionConfig(Config):
    pass

class DevelopmentConfig(Config):
    DEBUG = True

class TestingConfig(Config):
    SQLALCHEMY_DATABASE_URI = 'sqlite:///'
    TESTING = True
