# -*- coding: utf-8 -*-
"""
Created on Thu Jan  9 15:22:09 2020

@author: ShangFR
"""

# Create mysql database
DIALECT = 'mysql'
DRIVER = 'pymysql'
USERNAME = 'root'
PASSWORD = '123456'
HOST = '127.0.0.1'
PORT = '3306'
DATABASE = 'pythonflask'

#SQLALCHEMY_DATABASE_URI = "{}+{}://{}:{}@{}:{}/{}?charset=utf8".format(DIALECT, DRIVER, USERNAME, PASSWORD, HOST, PORT, DATABASE)


# Create dummy secrey key so we can use sessions
SECRET_KEY = '123456790'

# Create in-memory database sqlite
DATABASE_FILE = 'sample_db.sqlite'
SQLALCHEMY_DATABASE_URI = 'sqlite:///' + DATABASE_FILE
SQLALCHEMY_ECHO = True


