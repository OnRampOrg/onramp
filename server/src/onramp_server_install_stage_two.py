"""Complete actions needed for onramp REST server setup that require the newly
configured virtual environment.

This script is intended to be called solely by ../onramp_server_install.py.
"""

import os
import sys
import shutil
import sqlite3
from subprocess import call

db_filename = 'tmp/onramp_sqlite.db'
db_schema   = 'src/db/onramp_schema_sqlite.sql'

###################################################
if os.path.exists(db_filename):
    print "=" * 70
    print 'Warning: Database exists.'
    print "=" * 70

    response = raw_input('(R)emove and re-install or (A)bort? ')
    if response != 'R':
        sys.exit('Aborted')
    os.remove(db_filename)

print "=" * 70
print "Status: Creating Database (SQLite)"
print "=" * 70

conn = sqlite3.connect(db_filename)

with open(db_schema, 'rt') as f:
    schema = f.read()
conn.executescript(schema)

conn.commit()
conn.close()

os.system("cp "+db_filename+" "+db_filename+".bak")
