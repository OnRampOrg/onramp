--
-- Schema for our application
-- sqlite3 tmp/onramp_sqlite.db 
--

CREATE TABLE user (
    user_id integer primary key autoincrement not null,

    -- Data
    username text not null,
    password text not null,

    is_admin boolean DEFAULT false, -- 1 (true), 0 (false)

    -- Constraints
    UNIQUE(username)
);

-- TODO REMOVE ME
INSERT INTO user (username, password, is_admin) VALUES ('admin', 'admin123', 1);

CREATE TABLE workspace (
    workspace_id integer primary key autoincrement not null,

    -- Data
    workspace_name text not null,
    description text DEFAULT ''
);

CREATE TABLE pce (
    pce_id integer primary key autoincrement not null,

    -- Data
    pce_name text not null,
    description text DEFAULT ''
);

CREATE TABLE module (
    module_id integer primary key autoincrement not null,

    -- Data
    module_name text not null,
    description text DEFAULT ''
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

