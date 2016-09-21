#!my_onramp/server/src/env/bin/python -u

#
# 
#
import os
import sys
import requests
import json
from time import sleep

base_server_url = "http://flux.cs.uwlax.edu/~jjhursey/onramp/api"
base_pce_url    = "http://127.0.0.1:9071"

base_dir = "my_onramp/server/src"

######################################################
def _display_header(str):
    print "=" * 70
    print "Running: %s" % str
    print "=" * 70


def find_module_named(mod_name):
    _display_header("Find Module: " + mod_name)
    avail_mod = get_modules_avail()

    payload = {}
    for mod in avail_mod['modules']:
        if mod['mod_name'] == mod_name:
            payload = mod
            break

    return payload


######################################################
def get_modules_avail():
    global base_server_url
    global base_pce_url

    _display_header("GET Modules Avail")

    s = requests.Session()

    url = base_pce_url + "/modules/?state=Available"

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
def get_modules(id=None):
    global base_server_url
    global base_pce_url

    if id is None:
        _display_header("GET Modules")
    else:
        _display_header("GET Modules ("+str(id)+")")

    s = requests.Session()

    if id is None:
        url = base_pce_url + "/modules/"
    else:
        url = base_pce_url + "/modules/" + str(id)

    #url = url + "?apikey=" + str(cred['apikey'])

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
def add_module(id, module_name, mod_type, mod_path):
    global base_server_url
    global base_pce_url

    _display_header("Add Module ("+str(id)+", "+module_name+", "+mod_type+", "+mod_path+")")

    s = requests.Session()

    url = base_pce_url + "/modules"

    headers = {'content-type': 'application/json'}

    payload = {}

    payload['mod_id'] = id
    payload['mod_name'] = module_name
    payload['source_location'] = {}
    payload['source_location']['type'] = mod_type
    payload['source_location']['path'] = mod_path

    print "POST " + url
    print json.dumps(payload, sort_keys=True, indent=4, separators=(',',': '))

    r = s.post(url, data=json.dumps(payload), headers=headers)

    print "Result: %d: %s" % (r.status_code, r.headers['content-type'])

    work_id = None
    if r.status_code == 200:
        result = r.json()
        print json.dumps(r.json(), sort_keys=True, indent=4, separators=(',',': '))
    else:
        print "Reason: \"%s\"" % str(r.reason)

    return id

######################################################
def deploy_module(id):
    global base_server_url
    global base_pce_url

    _display_header("Deploy Module ("+str(id)+")")

    s = requests.Session()

    url = base_pce_url + "/modules/" + str(id)

    headers = {'content-type': 'application/json'}

    payload = {}

    print "POST " + url
    print json.dumps(payload, sort_keys=True, indent=4, separators=(',',': '))

    r = s.post(url, data=json.dumps(payload), headers=headers)

    print "Result: %d: %s" % (r.status_code, r.headers['content-type'])

    work_id = None
    if r.status_code == 200:
        result = r.json()
        print json.dumps(r.json(), sort_keys=True, indent=4, separators=(',',': '))
    else:
        print "Reason: \"%s\"" % str(r.reason)

    return id

######################################################
def get_cluster():
    global base_server_url
    global base_pce_url

    _display_header("GET Cluster")

    s = requests.Session()

    url = base_pce_url + "/cluster/"

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
def get_jobs(id=None):
    global base_server_url
    global base_pce_url

    if id is None:
        _display_header("GET Jobs")
    else:
        _display_header("GET Jobs ("+str(id)+")")

    s = requests.Session()

    if id is None:
        url = base_pce_url + "/jobs/"
    else:
        url = base_pce_url + "/jobs/" + str(id)

    #url = url + "?apikey=" + str(cred['apikey'])

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
def add_job(user, mod_id, job_id, run_name):
    global base_server_url
    global base_pce_url

    _display_header("Add Job ("+str(user)+", "+str(mod_id)+", "+str(job_id)+", "+str(run_name)+")")

    s = requests.Session()

    url = base_pce_url + "/jobs"

    headers = {'content-type': 'application/json'}

    payload = {}

    payload['username'] = user
    payload['mod_id']   = mod_id
    payload['job_id']   = job_id
    payload['run_name'] = run_name

    print "POST " + url
    print json.dumps(payload, sort_keys=True, indent=4, separators=(',',': '))

    r = s.post(url, data=json.dumps(payload), headers=headers)

    print "Result: %d: %s" % (r.status_code, r.headers['content-type'])

    work_id = None
    if r.status_code == 200:
        result = r.json()
        print json.dumps(r.json(), sort_keys=True, indent=4, separators=(',',': '))
    else:
        print "Reason: \"%s\"" % str(r.reason)

    return id


######################################################
if __name__ == '__main__':
    pce_root = "/home/jjhursey/work/onramp/my_onramp/"

    #
    # General information
    #
    #get_cluster()
    #get_modules_avail()
    get_modules()
    sys.exit(0)

    #
    # Find the module by name to get the path
    #
    #target_mod = find_module_named("mpi-ring")
    #print "Found: " + target_mod['mod_name'] + " at " + target_mod['source_location']['path']

    #
    # Deploy that module
    #
    module_id = 11
    #add_module(module_id, target_mod['mod_name'], target_mod['source_location']['type'], target_mod['source_location']['path'])
    #deploy_module(module_id)

    #
    # Check on the module state
    #
    #mod_state = get_modules(module_id)
    #print "State: " + mod_state['module']['state']

    #
    # Launch a job
    #
    job_id = 224
    #add_job("alice", module_id, job_id, "Alice's first run")
    #add_job("alice", module_id, job_id, "Alice_next_run")

    print "Waiting..."
    sleep(1)
    print "Checking..."
    get_jobs(job_id)

    sys.exit(0)


    print "="*70
    job_id = 111

    get_jobs(job_id)

    sys.exit(0)
