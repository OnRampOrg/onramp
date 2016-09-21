"""Functionality to support interacting with a SQLite Database
  Note the threading limitation at:
  http://cherrypy.readthedocs.org/en/latest/tutorials.html#tutorial-9-data-is-all-my-life
  This is why we open/close the connection around each call
"""

import os
import json
import onrampdb
import sqlite3
from threading import Lock
from time import sleep

class Database_sqlite(onrampdb.Database):
    _name = '[DB SQLite]'
    _lock = Lock()

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
        noop = 1

    def _connect(self):
        #self._logger.debug(self._name + " Connecting...")
        # Need a lock to protect a re-entrant thread situation
        self._lock.acquire()

        self._connection = sqlite3.connect( self._auth['filename'] )
        self._cursor = self._connection.cursor()

    def is_connected(self):
        is_connected = self._connection is not None
        return is_connected

    def disconnect(self):
        noop = 1

    def _disconnect(self):
        #self._logger.debug(self._name + " Disonnecting...")
        self._connection.commit()
        self._connection.close()
        self._connection = None
        self._cursor = None

        # Need a lock to protect a re-entrant thread situation
        self._lock.release()

    #######################################################################
    def _valid_id_check(self, sql, args):
        self._logger.debug(self._name + " " + sql)

        self._connect()
        self._cursor.execute(sql, args )
        row = self._cursor.fetchone()
        self._disconnect()

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

    def is_valid_job_id(self, job_id):
        sql = "SELECT job_id FROM job WHERE job_id = ?"
        args = (job_id, )
        return self._valid_id_check(sql, args)

    def is_valid_user_workspace(self, user_id, workspace_id):
        sql = "SELECT uw_pair_id FROM user_to_worksapce WHERE user_id = ? AND workspace_id = ?"
        args = (user_id, workspace_id)
        return self._valid_id_check(sql, args)

    def is_valid_pce_module(self, pce_id, module_id):
        sql = "SELECT pm_pair_id FROM module_to_pce WHERE pce_id = ? AND module_id = ?"
        args = (pce_id, module_id)
        return self._valid_id_check(sql, args)

    def is_valid_workspace_pce_module(self, workspace_id, pce_id, module_id):
        sql  = "SELECT wpm_pair_id "
        sql += " FROM workspace_to_pce_module AS W JOIN module_to_pce AS M ON W.pm_pair_id = M.pm_pair_id "
        sql += " WHERE W.workspace_id = ? AND M.pce_id = ? AND M.module_id = ?"
        args = (workspace_id, pce_id, module_id)
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
        
        self._connect()
        self._cursor.execute(sql, args )
        row = self._cursor.fetchone()
        self._disconnect()

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
        
        self._connect()
        self._cursor.execute(sql, args )
        rowid = self._cursor.lastrowid
        self._disconnect()

        return rowid

    def session_update(self, session_id):
        self._logger.debug(self._name + "session_update(" + str(session_id) + ")")

        sql = "UPDATE auth_session SET time_last_op = datetime('now','localtime') WHERE session_id = ?"
        args = (session_id, )

        self._logger.debug(self._name + " " + sql)
        
        self._connect()
        self._cursor.execute(sql, args )
        cnt = self._cursor.rowcount
        self._disconnect()

        if cnt > 0:
            return True
        else:
            return False

    def session_stop(self, session_id):
        self._logger.debug(self._name + "session_update(" + str(session_id) + ")")

        sql = "UPDATE auth_session SET time_logout = datetime('now','localtime') WHERE session_id = ?"
        args = (session_id, )

        self._logger.debug(self._name + " " + sql)
        
        self._connect()
        self._cursor.execute(sql, args )
        cnt = self._cursor.rowcount
        self._disconnect()

        if cnt > 0:
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
        
        self._connect()
        self._cursor.execute(sql, args )
        row = self._cursor.fetchone()
        self._disconnect()

        if row is None:
            return None
        else:
            return row[0]

    def add_user(self, username, password):
        self._logger.debug(self._name + "add_user(" + username + ")")

        sql = "INSERT INTO user (username, password, is_admin) VALUES (?, ?, 0)"
        args = (username, password)

        self._logger.debug(self._name + " " + sql)
        
        self._connect()
        self._cursor.execute(sql, args )
        rowid = self._cursor.lastrowid
        self._disconnect()

        return rowid

    def get_user_info(self, user_id=None):
        self._logger.debug(self._name + "get_user_info(" + str(user_id)+")")

        args = ()
        fields = ("user_id", "username", "full_name", "email", "is_admin", "is_enabled")
        sql = "SELECT "+ (",".join(fields)) + " FROM user"

        if user_id is not None:
            sql += " WHERE user_id = ?"
            args = (user_id, )

        self._logger.debug(self._name + " " + sql)
        
        self._connect()
        self._cursor.execute(sql, args )

        if user_id is not None:
            row = self._cursor.fetchone()
            self._disconnect()

            return {"fields": fields, "data": row }
        else:
            all_rows = self._cursor.fetchall()
            self._disconnect()

            if all_rows is None:
                return None
            self._logger.debug(self._name + " DEBUG " + str(type(all_rows)) + " and " + str(type(all_rows[0])) )
            clean_result = []
            for r in range( len(all_rows) ):
                row = []
                for i in range( len(all_rows[r]) ):
                    if i == 4 or i == 5:
                        row.append( True if all_rows[r][i] == 1 else False )
                    else:
                        row.append( all_rows[r][i] )
                clean_result.append(row)

            #return all_rows
            return {"fields" : fields, "data": clean_result }

    def get_user_workspaces(self, user_id):
        self._logger.debug(self._name + "get_user_workspaces(" + str(user_id)+")")

        args = ()
        fields = ("workspace_id", "workspace_name")

        sql  = "SELECT " + (', '.join(map('W.{0}'.format, fields)))
        sql += " FROM user_to_worksapce AS pair JOIN workspace AS W ON W.workspace_id = pair.workspace_id"
        sql += " WHERE pair.user_id = ?"

        args = (user_id, )

        self._logger.debug(self._name + " " + sql)
        
        self._connect()
        self._cursor.execute(sql, args )
        all_rows = self._cursor.fetchall()
        self._disconnect()

        return {"fields" : fields, "data": all_rows }

    def get_user_jobs(self, user_id, search_params):
        self._logger.debug(self._name + "get_user_jobs(" + str(user_id)+")")
        return self._find_jobs_by('user_id', user_id, search_params)


    ##########################################################
    def get_workspace_id(self, name):
        self._logger.debug(self._name + "get_workspace_id(" + name + ")")

        args = None
        sql = "SELECT workspace_id FROM workspace WHERE workspace_name = ?"
        args = (name, )

        self._logger.debug(self._name + " " + sql)
        
        self._connect()
        self._cursor.execute(sql, args )
        row = self._cursor.fetchone()
        self._disconnect()

        if row is None:
            return None
        else:
            return row[0]

    def add_workspace(self, name):
        self._logger.debug(self._name + "add_workspace(" + name + ")")

        sql = "INSERT INTO workspace (workspace_name) VALUES (?)"
        args = (name,)

        self._logger.debug(self._name + " " + sql)
        
        self._connect()
        self._cursor.execute(sql, args )
        rowid = self._cursor.lastrowid
        self._disconnect()

        return rowid

    def lookup_user_in_workspace(self, workspace_id, user_id):
        self._logger.debug(self._name + "lookup_user_in_workspace ("+ str(user_id) +" in " + str(workspace_id) + ")")

        args = None
        sql = "SELECT uw_pair_id FROM user_to_worksapce WHERE user_id = ? AND workspace_id = ?"
        args = (user_id, workspace_id)

        self._logger.debug(self._name + " " + sql)
        
        self._connect()
        self._cursor.execute(sql, args )
        row = self._cursor.fetchone()
        self._disconnect()

        if row is None:
            return None
        else:
            return row[0]

    def add_user_to_workspace(self, workspace_id, user_id):
        self._logger.debug(self._name + "add_user_to_workspace(" + str(user_id) +" in " + str(workspace_id) + ")")

        sql = "INSERT INTO user_to_worksapce (user_id, workspace_id) VALUES (?, ?)"
        args = (user_id, workspace_id)

        self._logger.debug(self._name + " " + sql)
        
        self._connect()
        self._cursor.execute(sql, args )
        rowid = self._cursor.lastrowid
        self._disconnect()

        return rowid

    def lookup_pair_in_workspace(self, workspace_id, pm_pair_id):
        self._logger.debug(self._name + "lookup_pair_in_workspace ("+str(pm_pair_id) +" in " + str(workspace_id) + ")")

        args = None
        sql = "SELECT wpm_pair_id FROM workspace_to_pce_module WHERE workspace_id = ? AND pm_pair_id = ?"
        args = (workspace_id, pm_pair_id)

        self._logger.debug(self._name + " " + sql)
        
        self._connect()
        self._cursor.execute(sql, args )
        row = self._cursor.fetchone()
        self._disconnect()

        if row is None:
            return None
        else:
            return row[0]

    def add_pair_to_workspace(self, workspace_id, pm_pair_id):
        self._logger.debug(self._name + "add_pair_to_workspace(" + str(pm_pair_id) +" in " + str(workspace_id) + ")")

        sql = "INSERT INTO workspace_to_pce_module (workspace_id, pm_pair_id) VALUES (?, ?)"
        args = (workspace_id, pm_pair_id)

        self._logger.debug(self._name + " " + sql)
        
        self._connect()
        self._cursor.execute(sql, args )
        rowid = self._cursor.lastrowid
        self._disconnect()

        return rowid

    def get_workspace_info(self, workspace_id=None):
        self._logger.debug(self._name + "get_workspace_info(" + str(workspace_id)+")")

        args = ()
        fields = ("workspace_id", "workspace_name", "description")
        sql = "SELECT "+ (",".join(fields)) + " FROM workspace"

        if workspace_id is not None:
            sql += " WHERE workspace_id = ?"
            args = (workspace_id, )

        self._logger.debug(self._name + " " + sql)
        
        self._connect()
        self._cursor.execute(sql, args )

        if workspace_id is not None:
            row = self._cursor.fetchone()
            self._disconnect()

            return {"fields": fields, "data": row }
        else:
            all_rows = self._cursor.fetchall()
            self._disconnect()

            if all_rows is None:
                return None
            return {"fields": fields, "data": all_rows }

    def get_workspace_doc(self, workspace_id):
        self._logger.debug(self._name + "get_workspace_doc(" + str(workspace_id)+")")

        return {"fields": None, "data": None }

    def get_workspace_users(self, workspace_id):
        self._logger.debug(self._name + "get_workspace_users(" + str(workspace_id)+")")

        fields = ("username", "user_id")
        sql  = "SELECT "+ (",".join(map('U.{0}'.format, fields)))
        sql += " FROM user_to_worksapce AS W"
        sql += " JOIN user AS U on U.user_id = W.user_id"
        sql += " WHERE workspace_id = ?"
        args = (workspace_id, )

        self._logger.debug(self._name + " " + sql)
        
        self._connect()
        self._cursor.execute(sql, args )
        all_rows = self._cursor.fetchall()
        self._disconnect()

        return {"fields": fields, "data": all_rows }

    def get_workspace_pairs(self, workspace_id):
        self._logger.debug(self._name + "get_workspace_pairs(" + str(workspace_id)+")")

        pce_fields = ("pce_id", "pce_name")
        module_fields = ("module_id", "module_name")
        fields = pce_fields + module_fields
        sql  = "SELECT "+ (",".join(map('P.{0}'.format, pce_fields))) + "," + (",".join(map('M.{0}'.format, module_fields)))
        sql += " FROM workspace_to_pce_module AS W JOIN module_to_pce AS PA ON W.pm_pair_id = PA.pm_pair_id"
        sql += " JOIN pce AS P on PA.pce_id = P.pce_id"
        sql += " JOIN module AS M on PA.module_id = M.module_id"
        sql += " WHERE workspace_id = ?"
        args = (workspace_id, )

        self._logger.debug(self._name + " " + sql)
        
        self._connect()
        self._cursor.execute(sql, args )
        all_rows = self._cursor.fetchall()
        self._disconnect()

        return {"fields": fields, "data": all_rows }

    def get_workspace_jobs(self, workspace_id, search_params):
        self._logger.debug(self._name + "get_workspace_jobs(" + str(workspace_id)+")")
        return self._find_jobs_by('workspace_id', workspace_id, search_params)


    ##########################################################
    def get_all_pce_ids(self):
        self._logger.debug(self._name + "get_all_pce_ids()")

        sql = "SELECT pce_id FROM pce"

        self._logger.debug(self._name + " " + sql)
        
        self._connect()
        self._cursor.execute(sql)
        all_rows = self._cursor.fetchall()
        self._disconnect()

        ids = []
        if all_rows is None:
            return ids
        else:
            for row in all_rows:
                ids.append(row[0])
            return ids

    def get_pce_id(self, info):
        self._logger.debug(self._name + "get_pce_id(" + info['name'] + ", "+info['url']+", "+str(info['port'])+")")

        args = None
        sql = "SELECT pce_id FROM pce WHERE pce_name = ? AND ip_addr = ? AND ip_port = ?"
        args = (info['name'], info['url'], info['port'] )

        self._logger.debug(self._name + " " + sql)
        
        self._connect()
        self._cursor.execute(sql, args )
        row = self._cursor.fetchone()
        self._disconnect()

        if row is None:
            return None

        return row[0]

    def add_pce(self, info):
        self._logger.debug(self._name + "add_pce(" + info['name'] + ", "+info['url']+", "+str(info['port'])+")")

        sql = "INSERT INTO pce (pce_name, ip_addr, ip_port, contact_info, location, description, pce_username) VALUES (?,?,?,?,?,?,?)"
        args = (info['name'],info['url'],info['port'],info['contact_info'],info['location'],info['description'],info['pce_username'])

        self._logger.debug(self._name + " " + sql)
        
        self._connect()
        self._cursor.execute(sql, args )
        rowid = self._cursor.lastrowid
        self._disconnect()

        return rowid

    def lookup_module_in_pce(self, pce_id, module_id):
        self._logger.debug(self._name + "lookup_module_in_pce ("+ str(module_id) +" in " + str(pce_id) + ")")

        args = None
        sql = "SELECT pm_pair_id FROM module_to_pce WHERE pce_id = ? AND module_id = ?"
        args = (pce_id, module_id)

        self._logger.debug(self._name + " " + sql)
        
        self._connect()
        self._cursor.execute(sql, args )
        row = self._cursor.fetchone()
        self._disconnect()

        if row is None:
            return None
        else:
            return row[0]

    def update_pce_state(self, pce_id, state):
        self._logger.debug(self._name + "update_pce_state (" + str(pce_id) +" in " + str(state) + ")")

        sql = "UPDATE pce SET state = ? WHERE pce_id = ?"
        args = (state, pce_id)

        self._logger.debug(self._name + " " + sql)
        
        self._connect()
        self._cursor.execute(sql, args )
        rowid = self._cursor.lastrowid
        self._disconnect()

        return rowid

    def add_module_to_pce(self, pce_id, module_id, src_location_type='local', src_location_path=''):
        self._logger.debug(self._name + "add_module_to_pce (" + str(module_id) +" in " + str(pce_id) + ")")

        sql = "INSERT INTO module_to_pce (pce_id, module_id, state, src_location_type, src_location_path) VALUES (?, ?, ?, ?, ?)"
        args = (pce_id, module_id, 0, src_location_type, src_location_path)

        self._logger.debug(self._name + " " + sql)
        
        self._connect()
        self._cursor.execute(sql, args )
        rowid = self._cursor.lastrowid
        self._disconnect()

        return rowid

    def update_pce_module_state(self, pce_id, module_id, state):
        self._logger.debug(self._name + "update_pce_module_state (" + str(pce_id) +" / "+str(module_id)+" in " + str(state) + ")")

        sql = "UPDATE module_to_pce SET state = ? WHERE pce_id = ? AND module_id = ?"
        args = (state, pce_id, module_id)

        self._logger.debug(self._name + " " + sql)
        
        self._connect()
        self._cursor.execute(sql, args )
        rowid = self._cursor.lastrowid
        self._disconnect()

        return rowid

    def get_pce_info(self, pce_id=None):
        self._logger.debug(self._name + "get_pce_info(" + str(pce_id)+")")

        args = ()
        fields = ("pce_id", "pce_name", "ip_addr", "ip_port", "state", "contact_info", "location", "description")
        sql = "SELECT "+ (",".join(fields)) + " FROM pce"

        if pce_id is not None:
            sql += " WHERE pce_id = ?"
            args = (pce_id, )

        self._logger.debug(self._name + " " + sql)
        
        self._connect()
        self._cursor.execute(sql, args )

        if pce_id is not None:
            row = self._cursor.fetchone()
            self._disconnect()

            return {"fields": fields, "data": row }
        else:
            all_rows = self._cursor.fetchall()
            self._disconnect()

            if all_rows is None:
                return None
            return {"fields": fields, "data": all_rows }

    def get_pce_state(self, pce_id):
        self._logger.debug(self._name + "get_pce_state(" + str(pce_id)+")")

        sql = "SELECT state FROM pce WHERE pce_id = ?"
        args = (pce_id, )

        self._logger.debug(self._name + " " + sql)
        
        self._connect()
        self._cursor.execute(sql, args )
        row = self._cursor.fetchone()
        self._disconnect()

        if row is not None:
            return row[0]
        else:
            return None

    def get_pce_doc(self, pce_id):
        self._logger.debug(self._name + "get_pce_doc(" + str(pce_id)+")")

        return {"fields": None, "data": None }

    def get_pce_workspaces(self, pce_id):
        self._logger.debug(self._name + "get_pce_pairs(" + str(pce_id)+")")

        fields = ("workspace_id", "workspace_name")
        sql  = "SELECT "+ (",".join(map('W.{0}'.format, fields)))
        sql += " FROM workspace_to_pce_module AS WA JOIN module_to_pce AS PA ON WA.pm_pair_id = PA.pm_pair_id"
        sql += " JOIN workspace AS W on WA.workspace_id = W.workspace_id"
        sql += " WHERE pce_id = ?"
        args = (pce_id, )

        self._logger.debug(self._name + " " + sql)
        
        self._connect()
        self._cursor.execute(sql, args )
        all_rows = self._cursor.fetchall()
        self._disconnect()

        return {"fields": fields, "data": all_rows }

    def get_pce_modules(self, pce_id, module_id=None):
        if module_id is None:
            self._logger.debug(self._name + "get_pce_modules(" + str(pce_id)+")")
        else:
            self._logger.debug(self._name + "get_pce_modules(" + str(pce_id)+", "+str(module_id)+")")

        fields = ("module_id", "module_name")
        pa_fields = ("state", "install_location", "is_visible", "src_location_type", "src_location_path")
        sql  = "SELECT "+ (",".join(map('M.{0}'.format, fields))) + ", " + (",".join(map('PA.{0}'.format, pa_fields)))
        sql += " FROM module_to_pce AS PA"
        sql += " JOIN module AS M on M.module_id = PA.module_id"
        sql += " WHERE pce_id = ?"
        if module_id is not None:
            sql += " AND PA.module_id = ?"
            args = (pce_id, module_id)
        else:
            args = (pce_id, )

        self._logger.debug(self._name + " " + sql)
        
        self._connect()
        self._cursor.execute(sql, args )
        if module_id is not None:
            all_rows = self._cursor.fetchone()
        else:
            all_rows = self._cursor.fetchall()
        self._disconnect()

        return {"fields": fields + pa_fields, "data": all_rows }

    def get_pce_jobs(self, pce_id, search_params):
        self._logger.debug(self._name + "get_pce_jobs(" + str(pce_id)+")")
        return self._find_jobs_by('pce_id', pce_id, search_params)

    ##########################################################
    def get_module_id(self, name):
        self._logger.debug(self._name + "get_module_id(" + name + ")")

        args = None
        sql = "SELECT module_id FROM module WHERE module_name = ?"
        args = (name, )

        self._logger.debug(self._name + " " + sql)
        
        self._connect()
        self._cursor.execute(sql, args )
        row = self._cursor.fetchone()
        self._disconnect()

        if row is None:
            return None

        return row[0]

    def add_module(self, name):
        self._logger.debug(self._name + "add_module(" + name + ")")

        sql = "INSERT INTO module (module_name) VALUES (?)"
        args = (name,)

        self._logger.debug(self._name + " " + sql)
        
        self._connect()
        self._cursor.execute(sql, args )
        rowid = self._cursor.lastrowid
        self._disconnect()

        return rowid

    def get_module_info(self, module_id=None):
        self._logger.debug(self._name + "get_module_info(" + str(module_id)+")")

        args = ()
        fields = ("module_id", "module_name", "version", "src_location", "description")
        sql = "SELECT "+ (",".join(fields)) + " FROM module"

        if module_id is not None:
            sql += " WHERE module_id = ?"
            args = (module_id, )

        self._logger.debug(self._name + " " + sql)
        
        self._connect()
        self._cursor.execute(sql, args )

        if module_id is not None:
            row = self._cursor.fetchone()
            self._disconnect()

            return {"fields": fields, "data": row }
        else:
            all_rows = self._cursor.fetchall()
            self._disconnect()

            if all_rows is None:
                return None
            return {"fields": fields, "data": all_rows }

    def get_module_doc(self, module_id):
        self._logger.debug(self._name + "get_module_doc(" + str(module_id)+")")

        return {"fields": None, "data": None }

    def get_module_pces(self, module_id):
        self._logger.debug(self._name + "get_module_pces(" + str(module_id)+")")

        fields = ("pce_id", "pce_name")
        sql  = "SELECT "+ (",".join(map('P.{0}'.format, fields)))
        sql += " FROM module_to_pce AS PA"
        sql += " JOIN pce AS P on P.pce_id = PA.pce_id"
        sql += " WHERE module_id = ?"
        args = (module_id, )

        self._logger.debug(self._name + " " + sql)
        
        self._connect()
        self._cursor.execute(sql, args )
        all_rows = self._cursor.fetchall()
        self._disconnect()

        return {"fields": fields, "data": all_rows }

    def get_module_jobs(self, module_id, search_params):
        self._logger.debug(self._name + "get_module_jobs(" + str(module_id)+")")
        return self._find_jobs_by('module_id', module_id, search_params)

    ##########################################################
    def find_job_id(self, user_id, workspace_id, pce_id, module_id, job_name):
        self._logger.debug(self._name + "find_job_id(" + str(user_id) + ", " + str(workspace_id) + ", " + str(pce_id) + ", " + str(module_id) + ", " + job_name + ")")

        args = None
        sql = "SELECT job_id FROM job WHERE user_id = ? AND workspace_id = ? AND pce_id = ? AND module_id = ? AND job_name = ?"
        args = (user_id, workspace_id, pce_id, module_id, job_name, )

        self._logger.debug(self._name + " " + sql)
        
        self._connect()
        self._cursor.execute(sql, args )
        row = self._cursor.fetchone()
        self._disconnect()

        if row is None:
            return None

        return row[0]


    def add_job(self, user_id, workspace_id, pce_id, module_id, job_data):
        self._logger.debug(self._name + "add_job(" + str(user_id) + ", " + str(workspace_id) + ", " + str(pce_id) + ", " + str(module_id) + ", " + job_data['job_name'] + ")")

        sql = "INSERT INTO job (user_id, workspace_id, pce_id, module_id, job_name) VALUES (?, ?, ?, ?, ?)"
        args = (user_id, workspace_id, pce_id, module_id, job_data['job_name'], )

        self._logger.debug(self._name + " " + sql)
        
        self._connect()
        self._cursor.execute(sql, args )
        rowid = self._cursor.lastrowid
        self._disconnect()

        return rowid

    def get_job_info(self, job_id=None, search_params={}):
        self._logger.debug(self._name + "get_job_info(" + str(job_id)+")")
        with_out_job_id = True
        if job_id is not None:
            with_out_job_id = False
            return self._find_jobs_by('job_id', job_id, search_params)

        args = ()
        fields = ("job_id", "user_id", "workspace_id", "pce_id", "module_id", "job_name", "state", "output_file")

        sql  = "SELECT " + (', '.join(fields))
        sql += " FROM job"

        wsql = ""
        largs = []

        for key, value in search_params.iteritems():
            self._logger.debug(self._name + "DEBUG Key = " + key)

            if len(largs) > 0:
                wsql += " AND "

            if type(value) is list:
                self._logger.debug(self._name + " Found a list value for the key " + key)

                wsql += "("
                for i in range(len(value)):
                    wsql += " " + key + "= ? "
                    largs.append(value[i])
                    if i != len(value)-1:
                        wsql += "OR"

                wsql += ")"
            else:
                wsql +=  key + " = ?"
                largs.append(value)

        if len(largs) > 0:
            sql += " WHERE " + wsql

        args = tuple(largs)

        self._logger.debug(self._name + " " + sql)
        
        self._connect()
        self._cursor.execute(sql, args )
        if with_out_job_id is False:
            all_rows = self._cursor.fetchone()
        else:
            all_rows = self._cursor.fetchall()
        self._disconnect()

        return {"fields" : fields, "data": all_rows }

    def get_job_data(self, job_id):
        self._logger.debug(self._name + "get_job_data(" + str(job_id)+")")
        with_out_job_id = True
        if job_id is not None:
            with_out_job_id = False
            return self._find_jobs_by('job_id', job_id, search_params)

        args = ()
        fields = ("output_file")

        sql  = "SELECT " + (', '.join(fields))
        sql += " FROM job"

        wsql = ""
        largs = []

        for key, value in search_params.iteritems():
            self._logger.debug(self._name + "DEBUG Key = " + key)

            if len(largs) > 0:
                wsql += " AND "

            if type(value) is list:
                self._logger.debug(self._name + " Found a list value for the key " + key)

                wsql += "("
                for i in range(len(value)):
                    wsql += " " + key + "= ? "
                    largs.append(value[i])
                    if i != len(value)-1:
                        wsql += "OR"

                wsql += ")"
            else:
                wsql +=  key + " = ?"
                largs.append(value)

        if len(largs) > 0:
            sql += " WHERE " + wsql

        args = tuple(largs)

        self._logger.debug(self._name + " " + sql)
        
        self._connect()
        self._cursor.execute(sql, args )
        if with_out_job_id is False:
            all_rows = self._cursor.fetchone()
        else:
            all_rows = self._cursor.fetchall()
        self._disconnect()

        return {"fields" : fields, "data": all_rows }


    def update_job_state(self, job_id, state):
        self._logger.debug(self._name + "update_job_state (" + str(job_id) +" in " + str(state) + ")")

        sql = "UPDATE job SET state = ? WHERE job_id = ?"
        args = (state, job_id)

        self._logger.debug(self._name + " " + sql)
        
        self._connect()
        self._cursor.execute(sql, args )
        rowid = self._cursor.lastrowid
        self._disconnect()

        return rowid


    ##########################################################
    def _find_jobs_by(self, id_str, id_value, search_params):
        args = ()
        fields = ("job_id", "user_id", "workspace_id", "pce_id", "module_id", "job_name", "state")

        sql  = "SELECT " + (', '.join(fields))
        sql += " FROM job"
        sql += " WHERE "+id_str+ " = ?"
        largs = []
        largs.append( id_value )
        for key, value in search_params.iteritems():
            if type(value) is list:
                self._logger.debug(self._name + " Found a list value for the key " + key)
                sql += " AND ("
                for i in range(len(value)):
                    sql += " " + key + "= ? "
                    largs.append(value[i])
                    if i != len(value)-1:
                        sql += "OR"

                sql += ")"
            else:
                sql += " AND " + key + " = ?"
                largs.append(value)

        args = tuple(largs)

        self._logger.debug(self._name + " " + sql)
        
        self._connect()
        self._cursor.execute(sql, args )
        if id_str == "job_id":
            all_rows = self._cursor.fetchone()
        else:
            all_rows = self._cursor.fetchall()
        self._disconnect()

        return {"fields" : fields, "data": all_rows }
