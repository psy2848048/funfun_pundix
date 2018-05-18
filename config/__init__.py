# -*- coding: utf-8 -*-
from datetime import timedelta
import os


class Config(object):
    VERSION = '0.1'
    DEBUG = True

    # Define the application directory
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))

    PORT = 5000
    HOST=''
    #SESSION_COOKIE_DOMAIN=".ciceron.me"
    #SESSION_COOKIE_PATH="/"

    #: Session
    SESSION_TYPE = 'redis'
    SESSION_COOKIE_NAME = "FunFunCookie"
    REMEMBER_COOKIE_DURATION = timedelta(days=15)
    # PERMANENT_SESSION_LIFETIME = timedelta(minutes=30)
    SECRET_KEY = os.urandom(24)

    #: Swagger
    #: SQLAlchemy, DB
    DATABASE_CONFIG = {
        'host': '',
        'dbname': '',
        'user': '',
        'password': '',
    }

    STEEM_POSTING_KEY = ['']

class ProdConfig(Config):
    PORT = 443
    HOST = ''
    #SESSION_COOKIE_DOMAIN=".ciceron.me"
    #SESSION_COOKIE_PATH="/"


class DevConfig(Config):
    PORT = 5001
    HOST = ''
    #SESSION_COOKIE_DOMAIN=".ciceron.me"
    #SESSION_COOKIE_PATH="/"

class TestConfig(Config):
    HOST = ''
    #SESSION_COOKIE_DOMAIN=".ciceron.me"
    #SESSION_COOKIE_PATH="/"
