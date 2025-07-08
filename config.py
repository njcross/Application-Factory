class DevelopmentConfig:
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'mysql+mysqlconnector://root:11Oval11@localhost/mydatabase'

class ProductionConfig:
    pass

class TestingConfig:
    pass