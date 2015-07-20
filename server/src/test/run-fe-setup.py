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
    user_cred = {}
    user_cred['id'] = None

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
    #run_full = False
    run_full = True

    if run_full == True:
        _display_header("Reset Database")
        os.system("cp ../../tmp/onramp_sqlite.db.bak ../../tmp/onramp_sqlite.db")

    # Login to the system
    admin_cred = do_login()
    print "Admin USER ID: " + str(admin_cred['id'])

    if run_full == True:
        # Add a User
        user_1_id = add_user(admin_cred, "alice", "notsecret123")
        user_1_id = add_user(admin_cred, "alice", "notother123")
        user_2_id = add_user(admin_cred, "bob",   "badpassword123")

        # Add a Workspace
        work_1_id = add_workspace(admin_cred, "CS270 Workspace")
        work_2_id = add_workspace(admin_cred, "CS441 Workspace")
        work_1_id = add_workspace(admin_cred, "CS270 Workspace")

        # Add a PCE
        pce_1_id = add_pce(admin_cred, "PCE AAA")
        pce_2_id = add_pce(admin_cred, "PCE BBB")
        pce_1_id = add_pce(admin_cred, "PCE AAA")

        # Add a Module
        module_1_id = add_module(admin_cred, "MODULE ZZZ")
        module_2_id = add_module(admin_cred, "MODULE YYY")
        module_1_id = add_module(admin_cred, "MODULE ZZZ")

        # Associate User with Workspace
        associate_user_with_workspace(admin_cred, user_1_id, work_1_id)
        associate_user_with_workspace(admin_cred, user_2_id, work_1_id)
        associate_user_with_workspace(admin_cred, user_2_id, work_2_id)

        # Associate Module with PCE
        associate_module_with_pce(admin_cred, module_1_id, pce_1_id)
        associate_module_with_pce(admin_cred, module_1_id, pce_2_id)
        associate_module_with_pce(admin_cred, module_2_id, pce_2_id)

        # Associate PCE / Module pair with workspace
        associate_pair_with_workspace(admin_cred, module_1_id, pce_1_id, work_1_id)
        associate_pair_with_workspace(admin_cred, module_1_id, pce_2_id, work_1_id)
        associate_pair_with_workspace(admin_cred, module_2_id, pce_2_id, work_1_id)

        associate_pair_with_workspace(admin_cred, module_1_id, pce_2_id, work_2_id)
        associate_pair_with_workspace(admin_cred, module_2_id, pce_2_id, work_2_id)

    else:
        user_1_id = 2
        user_2_id = 3
        work_1_id = 1
        work_2_id = 2
        pce_1_id  = 1
        pce_2_id  = 2
        module_1_id = 1
        module_2_id = 2



    sys.exit(0)
