import pymysql
import .config


def getConnection():
    return pymysql.connect(**(config.DATABASE_CONFIG))
