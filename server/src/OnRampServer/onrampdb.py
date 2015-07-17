"""Functionality to support interacting with an OnRamp Database

"""

import os
import json

class Database():

    def __init__(self, logger, auth):
        self._auth = auth
        self._logger = logger

    def is_connected(self):
        raise NotImplemented("Please implement this method")

    def connect(self):
        raise NotImplemented("Please implement this method")

    def disconnect(self):
        raise NotImplemented("Please implement this method")

    def get_user_id(self,username, password=None):
        raise NotImplemented("Please implement this method")

    def add_user(self,username, password):
        raise NotImplemented("Please implement this method")

from OnRampServer.onrampdb_sqlite import Database_sqlite

##########################################
_current_db = None
_known_db = { 'sqlite' : Database_sqlite }

##########################################
def define_database( logger, dbtype, auth ):
    global _current_db

    if dbtype not in _known_db:
        logger.critical( "Database: \"%s\" is not supported." % (dbtype) )
        return -1

    if _current_db is None:
        _current_db = _known_db[dbtype](logger, auth)

    return 0

##########################################
def user_login(username, password):
    db = _current_db
    db.connect()
    user_id = db.get_user_id(username, password)
    db.disconnect()
    return user_id

##########################################
def user_lookup(username):
    db = _current_db
    db.connect()
    user_id = db.get_user_id(username)
    db.disconnect()
    return user_id

##########################################
def user_add(username, password):
    db = _current_db
    db.connect()
    user_id = db.add_user(username, password)
    db.disconnect()
    return user_id
