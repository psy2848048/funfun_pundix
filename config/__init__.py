# -*- coding: utf-8 -*-
from datetime import timedelta
import json
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
    with open('env.json') as f:
        DATABASE_CONFIG = json.load(f)

    STEEM_POSTING_KEY = ['']

class ProdConfig(Config):
    PORT = 443
    HOST = ''


class DevConfig(Config):
    PORT = 5001
    HOST = ''

class TestConfig(Config):
    HOST = ''

