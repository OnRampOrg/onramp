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

    ##########################################################
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

    #######################################################################
    def _valid_id_check(self, sql, args):
        self._logger.debug(self._name + " " + sql)
        
        self._cursor.execute(sql, args )

        row = self._cursor.fetchone()
        if row is None:
            return False
        else:
            return True

    def is_valid_session_id(self, session_id):
        sql = "SELECT session_id FROM auth_session WHERE session_id = ?"
        args = (session_id, )
        return self._valid_id_check(sql, args)

    def is_valid_user_id(self, user_id):
        sql = "SELECT user_id FROM user WHERE user_id = ?"
        args = (user_id, )
        return self._valid_id_check(sql, args)

    def is_valid_workspace_id(self, workspace_id):
        sql = "SELECT workspace_id FROM workspace WHERE workspace_id = ?"
        args = (workspace_id, )
        return self._valid_id_check(sql, args)

    def is_valid_pce_id(self, pce_id):
        sql = "SELECT pce_id FROM pce WHERE pce_id = ?"
        args = (pce_id, )
        return self._valid_id_check(sql, args)

    def is_valid_module_id(self, module_id):
        sql = "SELECT module_id FROM module WHERE module_id = ?"
        args = (module_id, )
        return self._valid_id_check(sql, args)


    ##########################################################
    def is_active_session_id(self, session_id, user_id=None):
        self._logger.debug(self._name + "is_active_session_id(" + str(session_id) + ")")

        args = None
        if user_id is None:
            sql = "SELECT time_login, time_logout FROM auth_session WHERE session_id = ?"
            args = (session_id, )
        else:
            sql = "SELECT time_login, time_logout FROM auth_session WHERE session_id = ? AND user_id = ?"
            args = (session_id, user_id)

        self._logger.debug(self._name + " " + sql)
        
        self._cursor.execute(sql, args )

        row = self._cursor.fetchone()
        # No such session
        if row is None:
            return False
        # Session terminated (logout)
        elif row[1] is not None:
            return False
        # Is an old session -- TODO

        return True

    def session_start(self, user_id):
        self._logger.debug(self._name + "session_start(" + str(user_id) + ")")

        sql = "INSERT INTO auth_session (user_id, time_login, time_last_op) VALUES (?, datetime('now','localtime'), datetime('now','localtime'))"
        args = (user_id, )

        self._logger.debug(self._name + " " + sql)
        
        self._cursor.execute(sql, args )

        rowid = self._cursor.lastrowid

        return rowid

    def session_update(self, session_id):
        self._logger.debug(self._name + "session_update(" + str(session_id) + ")")

        sql = "UPDATE auth_session SET time_last_op = datetime('now','localtime') WHERE session_id = ?"
        args = (session_id, )

        self._logger.debug(self._name + " " + sql)
        
        self._cursor.execute(sql, args )

        if self._cursor.rowcount > 0:
            return True
        else:
            return False

    def session_stop(self, session_id):
        self._logger.debug(self._name + "session_update(" + str(session_id) + ")")

        sql = "UPDATE auth_session SET time_logout = datetime('now','localtime') WHERE session_id = ?"
        args = (session_id, )

        self._logger.debug(self._name + " " + sql)
        
        self._cursor.execute(sql, args )

        if self._cursor.rowcount > 0:
            return True
        else:
            return False

    #######################################################################
    def get_user_id(self, req_admin, username, password=None):
        self._logger.debug(self._name + "get_user_id(" + username + ", "+str(req_admin)+")")

        args = None
        sql = "SELECT user_id FROM user WHERE username = ?"
        args = (username, )
        if password is not None:
            sql += " AND password = ?"
            args = (username, password)

        if req_admin is True:
            sql += " AND is_admin = 1"

        self._logger.debug(self._name + " " + sql)
        
        self._cursor.execute(sql, args )

        row = self._cursor.fetchone()
        if row is None:
            return None
        else:
            return row[0]

    def add_user(self, username, password):
        self._logger.debug(self._name + "add_user(" + username + ")")

        sql = "INSERT INTO user (username, password, is_admin) VALUES (?, ?, 0)"
        args = (username, password)

        self._logger.debug(self._name + " " + sql)
        
        self._cursor.execute(sql, args )

        rowid = self._cursor.lastrowid

        return rowid


    ##########################################################
    def get_workspace_id(self, name):
        self._logger.debug(self._name + "get_workspace_id(" + name + ")")

        args = None
        sql = "SELECT workspace_id FROM workspace WHERE workspace_name = ?"
        args = (name, )

        self._logger.debug(self._name + " " + sql)
        
        self._cursor.execute(sql, args )

        row = self._cursor.fetchone()
        if row is None:
            return None
        else:
            return row[0]

    def add_workspace(self, name):
        self._logger.debug(self._name + "add_workspace(" + name + ")")

        sql = "INSERT INTO workspace (workspace_name) VALUES (?)"
        args = (name,)

        self._logger.debug(self._name + " " + sql)
        
        self._cursor.execute(sql, args )

        rowid = self._cursor.lastrowid

        return rowid

    def lookup_user_in_workspace(self, workspace_id, user_id):
        self._logger.debug(self._name + "lookup_user_in_workspace ("+ str(user_id) +" in " + str(workspace_id) + ")")

        args = None
        sql = "SELECT uw_pair_id FROM user_to_worksapce WHERE user_id = ? AND workspace_id = ?"
        args = (user_id, workspace_id)

        self._logger.debug(self._name + " " + sql)
        
        self._cursor.execute(sql, args )

        row = self._cursor.fetchone()
        if row is None:
            return None
        else:
            return row[0]

    def add_user_to_workspace(self, workspace_id, user_id):
        self._logger.debug(self._name + "add_user_to_workspace(" + str(user_id) +" in " + str(workspace_id) + ")")

        sql = "INSERT INTO user_to_worksapce (user_id, workspace_id) VALUES (?, ?)"
        args = (user_id, workspace_id)

        self._logger.debug(self._name + " " + sql)
        
        self._cursor.execute(sql, args )

        rowid = self._cursor.lastrowid

        return rowid

    def lookup_pair_in_workspace(self, workspace_id, pm_pair_id):
        self._logger.debug(self._name + "lookup_pair_in_workspace ("+str(pm_pair_id) +" in " + str(workspace_id) + ")")

        args = None
        sql = "SELECT wpm_pair_id FROM workspace_to_pce_module WHERE workspace_id = ? AND pm_pair_id = ?"
        args = (workspace_id, pm_pair_id)

        self._logger.debug(self._name + " " + sql)
        
        self._cursor.execute(sql, args )

        row = self._cursor.fetchone()
        if row is None:
            return None
        else:
            return row[0]

    def add_pair_to_workspace(self, workspace_id, pm_pair_id):
        self._logger.debug(self._name + "add_pair_to_workspace(" + str(pm_pair_id) +" in " + str(workspace_id) + ")")

        sql = "INSERT INTO workspace_to_pce_module (workspace_id, pm_pair_id) VALUES (?, ?)"
        args = (workspace_id, pm_pair_id)

        self._logger.debug(self._name + " " + sql)
        
        self._cursor.execute(sql, args )

        rowid = self._cursor.lastrowid

        return rowid


    ##########################################################
    def get_pce_id(self, name):
        self._logger.debug(self._name + "get_pce_id(" + name + ")")

        args = None
        sql = "SELECT pce_id FROM pce WHERE pce_name = ?"
        args = (name, )

        self._logger.debug(self._name + " " + sql)
        
        self._cursor.execute(sql, args )

        row = self._cursor.fetchone()
        if row is None:
            return None

        return row[0]

    def add_pce(self, name):
        self._logger.debug(self._name + "add_pce(" + name + ")")

        sql = "INSERT INTO pce (pce_name) VALUES (?)"
        args = (name,)

        self._logger.debug(self._name + " " + sql)
        
        self._cursor.execute(sql, args )

        rowid = self._cursor.lastrowid

        return rowid

    def lookup_module_in_pce(self, pce_id, module_id):
        self._logger.debug(self._name + "lookup_module_in_pce ("+ str(module_id) +" in " + str(pce_id) + ")")

        args = None
        sql = "SELECT pm_pair_id FROM module_to_pce WHERE pce_id = ? AND module_id = ?"
        args = (pce_id, module_id)

        self._logger.debug(self._name + " " + sql)
        
        self._cursor.execute(sql, args )

        row = self._cursor.fetchone()
        if row is None:
            return None
        else:
            return row[0]

    def add_module_to_pce(self, pce_id, module_id):
        self._logger.debug(self._name + "add_module_to_pce (" + str(module_id) +" in " + str(pce_id) + ")")

        sql = "INSERT INTO module_to_pce (pce_id, module_id) VALUES (?, ?)"
        args = (pce_id, module_id)

        self._logger.debug(self._name + " " + sql)
        
        self._cursor.execute(sql, args )

        rowid = self._cursor.lastrowid

        return rowid

    ##########################################################
    def get_module_id(self, name):
        self._logger.debug(self._name + "get_module_id(" + name + ")")

        args = None
        sql = "SELECT module_id FROM module WHERE module_name = ?"
        args = (name, )

        self._logger.debug(self._name + " " + sql)
        
        self._cursor.execute(sql, args )

        row = self._cursor.fetchone()
        if row is None:
            return None

        return row[0]

    def add_module(self, name):
        self._logger.debug(self._name + "add_module(" + name + ")")

        sql = "INSERT INTO module (module_name) VALUES (?)"
        args = (name,)

        self._logger.debug(self._name + " " + sql)
        
        self._cursor.execute(sql, args )

        rowid = self._cursor.lastrowid

        return rowid

    ##########################################################
