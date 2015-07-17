"""Functionality to support interacting with a SQLite Database

"""

import os
import json
import onrampdb
import sqlite3

class Database_sqlite(onrampdb.Database):
    _name = '[DB SQLite]'

    def __init__(self, logger, auth):
        onrampdb.Database.__init__(self, logger, auth)
        if os.path.exists(self._auth['filename']) == False:
            logger.critical(self._name + " Filename does not exist \""+self._auth['filename']+"\"")
        else:
            logger.debug(self._name + " Will connect with " + self._auth['filename'])
        self._connection = None
        self._cursor = None

    def connect(self):
        self._logger.debug(self._name + " Connecting...")
        if self.is_connected() == False:
            self._connection = sqlite3.connect( self._auth['filename'] )
            self._cursor = self._connection.cursor()

    def is_connected(self):
        is_connected = self._connection is not None
        #self._logger.debug(self._name + " Is connected = " + str(is_connected))
        return is_connected

    def disconnect(self):
        self._logger.debug(self._name + " Disonnecting...")
        if self.is_connected() == True:
            self._connection.commit()
            self._connection.close()
        self._connection = None
        self._cursor = None

    def get_user_id(self, username, password=None):
        self._logger.debug(self._name + "get_user_id(" + username + ")")
        self.is_connected()

        args = None
        if password is None:
            sql = "SELECT user_id FROM user WHERE username = ?"
            args = (username, )
        else:
            sql = "SELECT user_id FROM user WHERE username = ? AND password = ?"
            args = (username, password)

        self._logger.debug(self._name + " " + sql)
        
        self._cursor.execute(sql, args )

        row = self._cursor.fetchone()
        if row is None:
            return None

        return row[0]

    def add_user(self, username, password):
        self._logger.debug(self._name + "add_user(" + username + ")")
        self.is_connected()

        sql = "INSERT INTO user (username, password, is_admin) VALUES (?, ?, 0)"
        args = (username, password)

        self._logger.debug(self._name + " " + sql)
        
        self._cursor.execute(sql, args )

        rowid = self._cursor.lastrowid

        return rowid
