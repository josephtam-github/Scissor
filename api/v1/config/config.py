import os
from decouple import config
from datetime import timedelta


# SQLAlchemy configuration & instantiation
BASE_DIR = os.path.dirname(os.path.realpath(__file__))
db_name = 'scissor.db'

default_uri = "postgres://{}:{}@{}/{}".format('postgres', 'password', 'localhost:5432', db_name)
uri = os.environ.get('DATABASE_URL', default_uri)  # or other relevant config var
if uri and uri.startswith('postgres://'):
    uri = uri.replace('postgres://', 'postgresql://', 1)


class Config:
    SECRET_KEY = config('SECRET_KEY', os.urandom(24))
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(minutes=30)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=14)
    JWT_SECRET_KEY = config('JWT_SECRET_KEY', os.urandom(24))


class DevConfig(Config):
    DEBUG = True
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(BASE_DIR, db_name)


class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = True
    SQLALCHEMY_DATABASE_URI = 'sqlite://'


class ProdConfig(Config):
    SQLALCHEMY_DATABASE_URI = uri
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    DEBUG = config('DEBUG', False, cast=bool)


config_dict = {
    'dev': DevConfig,
    'test': TestConfig,
    'prod': ProdConfig
}
