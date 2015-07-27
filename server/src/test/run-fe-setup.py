#!../env/bin/python -u

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
def get_options(cred, level):
    global base_url

    _display_header("OPTIONS " + level)

    s = requests.Session()

    url = base_url + "/"+level+"/"

    url = url + "?apikey=" + str(cred['apikey'])

    print "OPTIONS " + url

    r = s.options(url)

    print "Result: %d: %s" % (r.status_code, r.headers['content-type'])

    result = {}
    if r.status_code == 200:
        result = r.json()
        print json.dumps(r.json(), sort_keys=True, indent=4, separators=(',',': '))
    else:
        print "Reason: \"%s\"" % str(r.reason)

    return result

######################################################
def get_users(cred, id=None, level=None, search=None):
    global base_url

    if id is None:
        _display_header("GET Users")
    elif level is None:
        _display_header("GET Users ("+str(id)+")")
    elif search is None:
        _display_header("GET Users ("+str(id)+"/"+level+")")
    else:
        _display_header("GET Users ("+str(id)+"/"+level+search+")")

    s = requests.Session()

    if id is None:
        url = base_url + "/users/"
    elif level is None:
        url = base_url + "/users/" + str(id)
    elif search is None:
        url = base_url + "/users/" + str(id) + "/" + level
    else:
        url = base_url + "/users/" + str(id) + "/" + level

    url = url + "?apikey=" + str(cred['apikey'])
    if search is not None:
        url = url + search

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
def get_workspaces(cred, id=None, level=None, search=None):
    global base_url

    if id is None:
        _display_header("GET Workspaces")
    elif level is None:
        _display_header("GET Workspaces ("+str(id)+")")
    elif search is None:
        _display_header("GET Workspaces ("+str(id)+"/"+level+")")
    else:
        _display_header("GET Workspaces ("+str(id)+"/"+level+search+")")

    s = requests.Session()

    if id is None:
        url = base_url + "/workspaces/"
    elif level is None:
        url = base_url + "/workspaces/" + str(id)
    elif search is None:
        url = base_url + "/workspaces/" + str(id) + "/" + level
    else:
        url = base_url + "/workspaces/" + str(id) + "/" + level

    url = url + "?apikey=" + str(cred['apikey'])
    if search is not None:
        url = url + search

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
def get_pces(cred, id=None, level=None, search=None):
    global base_url

    if id is None:
        _display_header("GET PCEs")
    elif level is None:
        _display_header("GET PCEs ("+str(id)+")")
    elif search is None:
        _display_header("GET PCEs ("+str(id)+"/"+level+")")
    else:
        _display_header("GET PCEs ("+str(id)+"/"+level+search+")")

    s = requests.Session()

    if id is None:
        url = base_url + "/pces/"
    elif level is None:
        url = base_url + "/pces/" + str(id)
    elif search is None:
        url = base_url + "/pces/" + str(id) + "/" + level
    else:
        url = base_url + "/pces/" + str(id) + "/" + level

    url = url + "?apikey=" + str(cred['apikey'])
    if search is not None:
        url = url + search

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
def get_modules(cred, id=None, level=None, search=None):
    global base_url

    if id is None:
        _display_header("GET Modules")
    elif level is None:
        _display_header("GET Modules ("+str(id)+")")
    elif search is None:
        _display_header("GET Modules ("+str(id)+"/"+level+")")
    else:
        _display_header("GET Modules ("+str(id)+"/"+level+search+")")

    s = requests.Session()

    if id is None:
        url = base_url + "/modules/"
    elif level is None:
        url = base_url + "/modules/" + str(id)
    elif search is None:
        url = base_url + "/modules/" + str(id) + "/" + level
    else:
        url = base_url + "/modules/" + str(id) + "/" + level

    url = url + "?apikey=" + str(cred['apikey'])
    if search is not None:
        url = url + search

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
def get_jobs(cred, id=None, level=None, search=None):
    global base_url

    if id is None:
        _display_header("GET Jobs")
    elif level is None:
        _display_header("GET Jobs ("+str(id)+")")
    elif search is None:
        _display_header("GET Jobs ("+str(id)+"/"+level+")")
    else:
        _display_header("GET Jobs ("+str(id)+"/"+level+search+")")

    s = requests.Session()

    if id is None:
        url = base_url + "/jobs/"
    elif level is None:
        url = base_url + "/jobs/" + str(id)
    elif search is None:
        url = base_url + "/jobs/" + str(id) + "/" + level
    else:
        url = base_url + "/jobs/" + str(id) + "/" + level

    url = url + "?apikey=" + str(cred['apikey'])
    if search is not None:
        url = url + search

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
def launch_job(admin_cred, user_id, work_id, pce_id, module_id, run_name):
    global base_url

    _display_header("Jobs: " + run_name)

    s = requests.Session()

    url = base_url + "/jobs"

    headers = {'content-type': 'application/json'}

    payload = {}

    payload['auth'] = admin_cred

    payload['info'] = {}
    payload['info']['user_id'] = user_id
    payload['info']['workspace_id'] = work_id
    payload['info']['pce_id'] = pce_id
    payload['info']['module_id'] = module_id
    payload['info']['job_name'] = run_name

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

def run_init_setup(username, password):
    # Login to the system
    admin_cred = do_login("admin", "admin123")
    print "Admin USER ID: " + str(admin_cred['user_id'])

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
    work_3_id = add_workspace(admin_cred, "CS370 Workspace")

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

    alice_cred = do_login("alice", "notsecret123")

    launch_job(alice_cred, user_1_id, work_u1_id, pce_1_id, module_1_id, "Run Alpha")
    launch_job(alice_cred, user_1_id, work_u1_id, pce_1_id, module_1_id, "Run Beta")
    launch_job(alice_cred, user_1_id, work_u1_id, pce_1_id, module_1_id, "Run Theta")

    do_logout(alice_cred)

    launch_job(admin_cred, user_2_id, work_u2_id, pce_1_id, module_1_id, "Run Alpha")
    launch_job(admin_cred, user_2_id, work_u2_id, pce_1_id, module_1_id, "Run Beta")
    launch_job(admin_cred, user_2_id, work_u2_id, pce_1_id, module_1_id, "Run Theta")

    launch_job(admin_cred, user_3_id, work_u3_id, pce_1_id, module_1_id, "Run Alpha")
    launch_job(admin_cred, user_3_id, work_u3_id, pce_1_id, module_1_id, "Run Beta")
    launch_job(admin_cred, user_3_id, work_u3_id, pce_1_id, module_1_id, "Run Theta")

    launch_job(admin_cred, user_1_id, work_1_id, pce_1_id, module_1_id, "Run Alpha")
    launch_job(admin_cred, user_2_id, work_1_id, pce_1_id, module_1_id, "Run Beta")
    launch_job(admin_cred, user_3_id, work_1_id, pce_1_id, module_1_id, "Run Theta")

    launch_job(admin_cred, user_1_id, work_2_id, pce_1_id, module_2_id, "Run Alpha")
    launch_job(admin_cred, user_2_id, work_2_id, pce_1_id, module_2_id, "Run Beta")
    launch_job(admin_cred, user_1_id, work_2_id, pce_2_id, module_1_id, "Run Theta")
    launch_job(admin_cred, user_2_id, work_2_id, pce_2_id, module_1_id, "Run Delta")
    launch_job(admin_cred, user_1_id, work_2_id, pce_2_id, module_3_id, "Run Theta num 3")
    launch_job(admin_cred, user_2_id, work_2_id, pce_2_id, module_3_id, "Run Delta num 3")

    launch_job(admin_cred, user_3_id, work_3_id, pce_1_id, module_3_id, "Run Alpha")
    launch_job(admin_cred, user_2_id, work_3_id, pce_1_id, module_3_id, "Run Beta")
    launch_job(admin_cred, user_3_id, work_3_id, pce_2_id, module_1_id, "Run Theta")
    launch_job(admin_cred, user_2_id, work_3_id, pce_2_id, module_1_id, "Run Delta")

    do_logout(admin_cred)

######################################################
if __name__ == '__main__':
    run_setup = False
    #run_setup = True

    if run_setup == True:
        _display_header("Reset Database")
        os.system("cp ../../tmp/onramp_sqlite.db.bak ../../tmp/onramp_sqlite.db")
        run_init_setup("admin", "admin123")

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

    #admin_cred = do_login("admin", "admin123")

    #get_users(alice_cred)
    #get_users(alice_cred, user_1_id)
    #get_users(alice_cred, user_1_id, "workspaces")
    #get_users(alice_cred, user_1_id, "jobs")
    #get_users(alice_cred, user_1_id, "jobs", "&workspace=5&pce=1&module=2")
    #get_users(alice_cred, user_1_id, "jobs", "&workspace=5&pce=1&module=2&state=0")
    #get_users(alice_cred, user_1_id, "jobs", "&workspace=5&pce=1&module=2&state=1&state=0")

    #get_workspaces(alice_cred)
    #get_workspaces(alice_cred, work_1_id)
    #get_workspaces(alice_cred, work_1_id, "docs")
    #get_workspaces(alice_cred, work_1_id, "users")
    #get_workspaces(alice_cred, work_1_id, "pcemodulepairs")
    #get_workspaces(alice_cred, work_1_id, "jobs")
    #get_workspaces(alice_cred, work_1_id, "jobs", "&user=2&pce=1&module=1")
    #get_workspaces(alice_cred, work_1_id, "jobs", "&user=2&pce=1&module=1&state=0")
    #get_workspaces(alice_cred, work_1_id, "jobs", "&user=2&pce=1&module=1&state=0&state=1")

    #get_pces(alice_cred)
    #get_pces(alice_cred, pce_1_id)
    #get_pces(alice_cred, pce_1_id, "docs")
    #get_pces(alice_cred, pce_1_id, "workspaces")
    #get_pces(alice_cred, pce_1_id, "modules")
    #get_pces(alice_cred, pce_1_id, "jobs")
    #get_pces(alice_cred, pce_1_id, "jobs", "&user=3&workspace=6&module=3")
    #get_pces(alice_cred, pce_1_id, "jobs", "&user=3&workspace=6&module=3&state=0")
    #get_pces(alice_cred, pce_1_id, "jobs", "&user=3&workspace=6&module=3&state=0&state=1")

    #get_modules(alice_cred)
    #get_modules(alice_cred, module_1_id)
    #get_modules(alice_cred, module_1_id, "docs")
    #get_modules(alice_cred, module_1_id, "pces")
    #get_modules(alice_cred, module_1_id, "jobs")
    #get_modules(alice_cred, module_1_id, "jobs", "&user=3&workspace=6&pce=2")
    #get_modules(alice_cred, module_1_id, "jobs", "&user=3&workspace=6&pce=2&state=0")
    #get_modules(alice_cred, module_1_id, "jobs", "&user=3&workspace=6&pce=2&state=0&state=1")

    #get_jobs(alice_cred)
    #get_jobs(alice_cred, search="&user=4")
    #get_jobs(alice_cred, search="&user=4&workspace=6")
    #get_jobs(alice_cred, search="&user=4&workspace=6&pce=2&module=1")
    #get_jobs(alice_cred, search="&user=4&workspace=6&pce=2&module=1&state=0")
    #get_jobs(alice_cred, search="&user=4&workspace=6&pce=2&module=1&state=0&state=1")
    #get_jobs(alice_cred, id=21)
    #get_jobs(alice_cred, id=21, level="data")

    get_options(alice_cred, "pces")
    get_options(alice_cred, "modules")
    get_options(alice_cred, "jobs")


    #do_logout(admin_cred)
    #do_logout(alice_cred)

    sys.exit(0)
