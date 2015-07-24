#!../env/bin/python

#
# One Time setup for the Front End (while admin in not implemented)
#
import os
import sys
import requests
import json

server_addr = "138.49.30.31"
server_port = 9090

base_url = "http://flux.cs.uwlax.edu/~jjhursey/onramp/api"

######################################################
def _display_header(str):
    print "=" * 70
    print "Running: %s" % str
    print "=" * 70

######################################################
def rough(cred, id):
    global base_url

    _display_header("GET Users")

    s = requests.Session()

    url = base_url + "/users/" + str(id)

    url = url + "?apikey=" + str(cred['apikey'])

    print "GET " + url

    r = s.get(url)

    print "Result: %d: %s" % (r.status_code, r.headers['content-type'])

    result = {}
    if r.status_code == 200:
        result = r.json()
        print json.dumps(r.json(), sort_keys=True, indent=4, separators=(',',': '))
    else:
        print "Reason: \"%s\"" % str(r.reason)

    return result

######################################################
def do_logout(admin_cred):
    global base_url

    _display_header("Logout")

    s = requests.Session()

    url = base_url + "/logout"

    headers = {'content-type': 'application/json'}

    payload = {}

    payload['auth'] = admin_cred

    print "POST " + url
    print json.dumps(payload, sort_keys=True, indent=4, separators=(',',': '))

    r = s.post(url, data=json.dumps(payload), headers=headers)

    print "Result: %d: %s" % (r.status_code, r.headers['content-type'])
    user_cred = {}

    if r.status_code == 200:
        result = r.json()
        print json.dumps(r.json(), sort_keys=True, indent=4, separators=(',',': '))
    else:
        print "Reason: \"%s\"" % str(r.reason)

    return user_cred

######################################################
def do_login(username, password):
    global base_url

    _display_header("Login")

    s = requests.Session()

    url = base_url + "/login"

    headers = {'content-type': 'application/json'}

    payload = {}

    payload['username'] = username
    payload['password'] = password

    print "POST " + url
    print json.dumps(payload, sort_keys=True, indent=4, separators=(',',': '))

    r = s.post(url, data=json.dumps(payload), headers=headers)

    print "Result: %d: %s" % (r.status_code, r.headers['content-type'])
    user_cred = {}

    if r.status_code == 200:
        result = r.json()
        print json.dumps(r.json(), sort_keys=True, indent=4, separators=(',',': '))
        for key in result["auth"]:
            user_cred[key] = result["auth"][key]
    else:
        print "Reason: \"%s\"" % str(r.reason)

    return user_cred

######################################################
def add_user(admin_cred, username, password):
    global base_url

    _display_header("Add User ("+username+") ("+password+")")

    s = requests.Session()

    url = base_url + "/admin/user"

    headers = {'content-type': 'application/json'}

    payload = {}

    payload['auth'] = admin_cred

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
def add_workspace(admin_cred, wname):
    global base_url

    _display_header("Add Workspace ("+wname+")")

    s = requests.Session()

    url = base_url + "/admin/workspace"

    headers = {'content-type': 'application/json'}

    payload = {}

    payload['auth'] = admin_cred

    payload['name'] = wname

    print "POST " + url
    print json.dumps(payload, sort_keys=True, indent=4, separators=(',',': '))

    r = s.post(url, data=json.dumps(payload), headers=headers)

    print "Result: %d: %s" % (r.status_code, r.headers['content-type'])

    work_id = None
    if r.status_code == 200:
        result = r.json()
        print json.dumps(r.json(), sort_keys=True, indent=4, separators=(',',': '))
        work_id = result["workspace"]["id"]
    else:
        print "Reason: \"%s\"" % str(r.reason)

    return work_id

######################################################
def add_pce(admin_cred, pce_name):
    global base_url

    _display_header("Add PCE ("+pce_name+")")

    s = requests.Session()

    url = base_url + "/admin/pce"

    headers = {'content-type': 'application/json'}

    payload = {}

    payload['auth'] = admin_cred

    payload['name'] = pce_name

    print "POST " + url
    print json.dumps(payload, sort_keys=True, indent=4, separators=(',',': '))

    r = s.post(url, data=json.dumps(payload), headers=headers)

    print "Result: %d: %s" % (r.status_code, r.headers['content-type'])

    work_id = None
    if r.status_code == 200:
        result = r.json()
        print json.dumps(r.json(), sort_keys=True, indent=4, separators=(',',': '))
        work_id = result["pce"]["id"]
    else:
        print "Reason: \"%s\"" % str(r.reason)

    return work_id

######################################################
def add_module(admin_cred, module_name):
    global base_url

    _display_header("Add Module ("+module_name+")")

    s = requests.Session()

    url = base_url + "/admin/module"

    headers = {'content-type': 'application/json'}

    payload = {}

    payload['auth'] = admin_cred

    payload['name'] = module_name

    print "POST " + url
    print json.dumps(payload, sort_keys=True, indent=4, separators=(',',': '))

    r = s.post(url, data=json.dumps(payload), headers=headers)

    print "Result: %d: %s" % (r.status_code, r.headers['content-type'])

    work_id = None
    if r.status_code == 200:
        result = r.json()
        print json.dumps(r.json(), sort_keys=True, indent=4, separators=(',',': '))
        work_id = result["module"]["id"]
    else:
        print "Reason: \"%s\"" % str(r.reason)

    return work_id

######################################################
def associate_user_with_workspace(admin_cred, user_id, work_id):
    global base_url

    _display_header("Associate User with Workspace ("+str(user_id)+" to "+str(work_id)+")")

    s = requests.Session()

    url = base_url + "/admin/workspace/"+str(work_id)+"/user/"+str(user_id)

    headers = {'content-type': 'application/json'}

    payload = {}

    payload['auth'] = admin_cred

    #payload['name'] = module_name

    print "POST " + url
    print json.dumps(payload, sort_keys=True, indent=4, separators=(',',': '))

    r = s.post(url, data=json.dumps(payload), headers=headers)

    print "Result: %d: %s" % (r.status_code, r.headers['content-type'])

    does_exist = False
    if r.status_code == 200:
        result = r.json()
        print json.dumps(r.json(), sort_keys=True, indent=4, separators=(',',': '))
        does_exist = result["workspace"]["exists"]
    else:
        print "Reason: \"%s\"" % str(r.reason)

    return does_exist

######################################################
def associate_module_with_pce(admin_cred, module_id, pce_id):
    global base_url

    _display_header("Associate Module with PCE ("+str(module_id)+" to "+str(pce_id)+")")

    s = requests.Session()

    url = base_url + "/admin/pce/"+str(pce_id)+"/module/"+str(module_id)

    headers = {'content-type': 'application/json'}

    payload = {}

    payload['auth'] = admin_cred

    #payload['name'] = module_name

    print "POST " + url
    print json.dumps(payload, sort_keys=True, indent=4, separators=(',',': '))

    r = s.post(url, data=json.dumps(payload), headers=headers)

    print "Result: %d: %s" % (r.status_code, r.headers['content-type'])

    does_exist = False
    if r.status_code == 200:
        result = r.json()
        print json.dumps(r.json(), sort_keys=True, indent=4, separators=(',',': '))
        does_exist = result["pce"]["exists"]
    else:
        print "Reason: \"%s\"" % str(r.reason)

    return does_exist

######################################################
def associate_pair_with_workspace(admin_cred, module_id, pce_id, workspace_id):
    global base_url

    _display_header("Associate Pair with Workspace ("+str(module_id)+"/"+str(pce_id)+" to "+str(workspace_id)+")")

    s = requests.Session()

    url = base_url + "/admin/workspace/"+str(workspace_id)+"/pcemodulepairs/"+str(pce_id)+"/"+str(module_id)

    headers = {'content-type': 'application/json'}

    payload = {}

    payload['auth'] = admin_cred

    #payload['name'] = module_name

    print "POST " + url
    print json.dumps(payload, sort_keys=True, indent=4, separators=(',',': '))

    r = s.post(url, data=json.dumps(payload), headers=headers)

    print "Result: %d: %s" % (r.status_code, r.headers['content-type'])

    does_exist = False
    if r.status_code == 200:
        result = r.json()
        print json.dumps(r.json(), sort_keys=True, indent=4, separators=(',',': '))
        does_exist = result["workspace"]["exists"]
    else:
        print "Reason: \"%s\"" % str(r.reason)

    return does_exist

######################################################
if __name__ == '__main__':
    run_full = False
    #run_full = True

    if run_full == True:
        _display_header("Reset Database")
        os.system("cp ../../tmp/onramp_sqlite.db.bak ../../tmp/onramp_sqlite.db")

    # Login to the system
    admin_cred = do_login("admin", "admin123")
    print "Admin USER ID: " + str(admin_cred['user_id'])

    if run_full == True:
        # Add a User
        user_1_id = add_user(admin_cred, "alice", "notsecret123")
        user_2_id = add_user(admin_cred, "bob",   "notother123")
        user_3_id = add_user(admin_cred, "cali",  "badpassword123")

        # Add a Workspace
        work_u1_id = add_workspace(admin_cred, "alice User Workspace")
        work_u2_id = add_workspace(admin_cred, "bob User Workspace")
        work_u3_id = add_workspace(admin_cred, "cali User Workspace")
        work_1_id = add_workspace(admin_cred, "CS270 Workspace")
        work_2_id = add_workspace(admin_cred, "CS441 Workspace")
        work_3_id = add_workspace(admin_cred, "CS270 Workspace")

        # Add a PCE
        pce_1_id = add_pce(admin_cred, "PCE One")
        pce_2_id = add_pce(admin_cred, "PCE Two")
        pce_3_id = add_pce(admin_cred, "PCE Three")

        # Add a Module
        module_1_id = add_module(admin_cred, "MODULE AAA")
        module_2_id = add_module(admin_cred, "MODULE BBB")
        module_3_id = add_module(admin_cred, "MODULE CCC")

        # Associate User with Workspace
        associate_user_with_workspace(admin_cred, user_1_id, work_u1_id)
        associate_user_with_workspace(admin_cred, user_2_id, work_u2_id)
        associate_user_with_workspace(admin_cred, user_3_id, work_u3_id)

        associate_user_with_workspace(admin_cred, user_1_id, work_1_id)
        associate_user_with_workspace(admin_cred, user_2_id, work_1_id)
        associate_user_with_workspace(admin_cred, user_3_id, work_1_id)

        associate_user_with_workspace(admin_cred, user_1_id, work_2_id)
        associate_user_with_workspace(admin_cred, user_2_id, work_2_id)

        associate_user_with_workspace(admin_cred, user_2_id, work_3_id)
        associate_user_with_workspace(admin_cred, user_3_id, work_3_id)

        # Associate Module with PCE
        associate_module_with_pce(admin_cred, module_1_id, pce_1_id)
        associate_module_with_pce(admin_cred, module_2_id, pce_1_id)
        associate_module_with_pce(admin_cred, module_3_id, pce_1_id)

        associate_module_with_pce(admin_cred, module_1_id, pce_2_id)
        associate_module_with_pce(admin_cred, module_3_id, pce_2_id)

        associate_module_with_pce(admin_cred, module_2_id, pce_3_id)

        # Associate PCE / Module pair with workspace
        associate_pair_with_workspace(admin_cred, module_1_id, pce_1_id, work_u1_id)
        associate_pair_with_workspace(admin_cred, module_1_id, pce_1_id, work_u2_id)
        associate_pair_with_workspace(admin_cred, module_1_id, pce_1_id, work_u3_id)
        associate_pair_with_workspace(admin_cred, module_1_id, pce_1_id, work_1_id)

        associate_pair_with_workspace(admin_cred, module_2_id, pce_1_id, work_1_id)
        associate_pair_with_workspace(admin_cred, module_2_id, pce_1_id, work_2_id)

        associate_pair_with_workspace(admin_cred, module_3_id, pce_1_id, work_1_id)
        associate_pair_with_workspace(admin_cred, module_3_id, pce_1_id, work_3_id)

        associate_pair_with_workspace(admin_cred, module_1_id, pce_2_id, work_1_id)
        associate_pair_with_workspace(admin_cred, module_1_id, pce_2_id, work_2_id)
        associate_pair_with_workspace(admin_cred, module_1_id, pce_2_id, work_3_id)

        associate_pair_with_workspace(admin_cred, module_3_id, pce_2_id, work_1_id)
        associate_pair_with_workspace(admin_cred, module_3_id, pce_2_id, work_2_id)

        associate_pair_with_workspace(admin_cred, module_2_id, pce_3_id, work_1_id)

    else:
        user_1_id = 2
        user_2_id = 3
        user_3_id = 4

        work_u1_id = 1
        work_u2_id = 2
        work_u3_id = 3
        work_1_id = 4
        work_2_id = 5
        work_3_id = 6

        pce_1_id  = 1
        pce_2_id  = 2
        pce_3_id  = 3

        module_1_id = 1
        module_2_id = 2
        module_3_id = 3

    alice_cred = do_login("alice", "notsecret123")
    rough(alice_cred, user_1_id)
    #user_N_id = add_user(alice_cred, "fail",   "shouldfail")

    #do_logout(admin_cred)
    #do_logout(alice_cred)

    sys.exit(0)
