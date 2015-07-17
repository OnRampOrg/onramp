#!../env/bin/python

#
# One Time setup for the Front End (while admin in not implemented)
#
import sys
import requests
import json

server_addr = "138.49.30.31"
server_port = 9090

base_url = "http://flux.cs.uwlax.edu/~jjhursey/onramp/api/"

######################################################
def _display_header(str):
    print "=" * 70
    print "Running: %s" % str
    print "=" * 70

######################################################
def do_login():
    global base_url

    _display_header("Login")

    s = requests.Session()

    url = base_url + "/login"

    headers = {'content-type': 'application/json'}

    payload = {}

    payload['username'] = 'admin'
    payload['password'] = 'admin123'

    print "POST " + url
    print json.dumps(payload, sort_keys=True, indent=4, separators=(',',': '))

    r = s.post(url, data=json.dumps(payload), headers=headers)

    print "Result: %d: %s" % (r.status_code, r.headers['content-type'])
    user_id = None
    if r.status_code == 200:
        result = r.json()
        print json.dumps(r.json(), sort_keys=True, indent=4, separators=(',',': '))
        user_id = result["auth"]["id"]
    else:
        print "Reason: \"%s\"" % str(r.reason)

    return user_id

######################################################
def add_user(admin_user_id, username, password):
    global base_url

    _display_header("Add User ("+username+") ("+password+")")

    s = requests.Session()

    url = base_url + "/admin/user"

    headers = {'content-type': 'application/json'}

    payload = {}

    payload['auth'] = {}
    payload['auth']['id'] = admin_user_id

    payload['username'] = username
    payload['password'] = password

    print "POST " + url
    print json.dumps(payload, sort_keys=True, indent=4, separators=(',',': '))

    r = s.post(url, data=json.dumps(payload), headers=headers)

    print "Result: %d: %s" % (r.status_code, r.headers['content-type'])
    user_id = None
    if r.status_code == 200:
        result = r.json()
        print json.dumps(r.json(), sort_keys=True, indent=4, separators=(',',': '))
        user_id = result["user"]["id"]
    else:
        print "Reason: \"%s\"" % str(r.reason)

    return user_id

######################################################
if __name__ == '__main__':
    # Login to the system
    admin_user_id = do_login()
    print "Admin USER ID: " + str(admin_user_id)
    # Add a User
    user_id = add_user(admin_user_id, "alice", "notsecret123")
    #user_id = add_user(admin_user_id, "bob",   "badpassword123")
    # Add a Workspace
    # Add a PCE
    # Add a Module
    # Associate User with Workspace
    # Associate Module with PCE
    # Associate PCE / Module pair with workspace

    sys.exit(0)
