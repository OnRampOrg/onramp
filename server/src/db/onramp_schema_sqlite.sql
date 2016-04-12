--
-- Schema for our application
-- sqlite3 tmp/onramp_sqlite.db 
--

CREATE TABLE user (
    user_id integer primary key autoincrement not null,

    -- Data
    username   text not null,
    password   text not null,

    full_name  text DEFAULT '',
    email      text DEFAULT '',
    
    is_admin   boolean DEFAULT 0, -- 1 (true), 0 (false)
    is_enabled boolean DEFAULT 1, -- 1 (true), 0 (false)

    -- Constraints
    UNIQUE(username)
);

-- TODO REMOVE ME
INSERT INTO user (username, password, full_name, is_admin) VALUES ('admin', 'admin123', 'Dummy Admin', 1);

CREATE TABLE workspace (
    workspace_id integer primary key autoincrement not null,

    -- Data
    workspace_name text not null,
    description text DEFAULT '',

    -- TODO: Files?

    -- Constraints
    UNIQUE(workspace_name)
);

CREATE TABLE pce (
    pce_id integer primary key autoincrement not null,

    -- Data
    pce_name text not null,

    ip_addr  text DEFAULT '127.0.0.1',
    ip_port  integer DEFAULT '0',

    state integer DEFAULT 0, -- See onrampdb.py for state values

    contact_info text DEFAULT '',
    location     text DEFAULT '',
    description  text DEFAULT '',

    -- TODO: UNIX Auth?
    pce_username text DEFAULT 'onramp',

    -- TODO: Files?

    -- Constraints
    UNIQUE(pce_name)
);

CREATE TABLE module (
    module_id integer primary key autoincrement not null,

    -- Data
    module_name text not null,

    version text DEFAULT '',
    src_location text DEFAULT '',
    description text DEFAULT '',

    -- Constraints
    UNIQUE(module_name)
);

CREATE TABLE job (
    job_id integer primary key autoincrement not null,

    -- Tied to what other IDs
    user_id integer,
    workspace_id integer,
    pce_id integer,
    module_id integer,

    -- Other data
    job_name text not null,

    state integer DEFAULT 0, -- See onrampdb.py for state values
    output_file text DEFAULT '',

    -- TODO: Run parameters (JSON)
    -- TODO: Files
    -- TODO: Runtime

    -- Constraints
    FOREIGN KEY(user_id) REFERENCES user(user_id),
    FOREIGN KEY(workspace_id) REFERENCES workspace(workspace_id),
    FOREIGN KEY(pce_id) REFERENCES pce(pce_id),
    FOREIGN KEY(module_id) REFERENCES module(module_id)
);

-- Users that belong to a workspace
CREATE TABLE user_to_worksapce (
    uw_pair_id integer primary key autoincrement not null,

    user_id integer,
    workspace_id integer,

    -- Constraints
    UNIQUE(user_id, workspace_id),
    FOREIGN KEY(user_id) REFERENCES user(user_id),
    FOREIGN KEY(workspace_id) REFERENCES workspace(workspace_id)
);

-- Modules on a PCE
CREATE TABLE module_to_pce (
    pm_pair_id integer primary key autoincrement not null,

    pce_id integer,
    module_id integer,

    -- Other data
    state integer DEFAULT 0, -- See onrampdb.py for state values

    src_location_type text DEFAULT 'local',
    src_location_path text DEFAULT '',

    install_location text DEFAULT '',
    is_visible boolean DEFAULT 1, -- 1 (true), 0 (false)

    -- TODO: ConfigObj file

    -- Constraints
    UNIQUE(pce_id, module_id),
    FOREIGN KEY(pce_id) REFERENCES pce(pce_id),
    FOREIGN KEY(module_id) REFERENCES module(module_id)
);

-- Workspaces connected to a PCE / Module pair
CREATE TABLE workspace_to_pce_module (
    wpm_pair_id integer primary key autoincrement not null,
    workspace_id integer,
    pm_pair_id integer,

    -- Constraints
    UNIQUE(workspace_id, pm_pair_id),
    FOREIGN KEY(workspace_id) REFERENCES workspace(workspace_id),
    FOREIGN KEY(pm_pair_id) REFERENCES module_to_pce(pm_pair_id)
);

-- Session information
CREATE TABLE auth_session (
   session_id integer primary key autoincrement not null,

   -- Data
   user_id integer,
   time_login   timestamp DEFAULT (datetime('now','localtime')),
   time_last_op timestamp DEFAULT (datetime('now','localtime')),
   time_logout  timestamp DEFAULT NULL,

   -- Constraints
    FOREIGN KEY(user_id) REFERENCES user(user_id)
);
