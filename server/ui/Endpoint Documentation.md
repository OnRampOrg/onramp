# admin/Dashboard

### /GetUsers/
	Retrieve all OnRamp Users
### /GetJobs/
	Retrieve basic info for all OnRamp Jobs
### /GetWorkspaces/
	Retrieve all configured workspaces
### /GetPces/
	Retrieve all configured PCEs
### /GetModules/
	Retrieve all loaded modules

---
# admin/Jobs

### /GetAll/
	Retrieve all jobs
### /GetOne/
**Description:**
Retrieve a specific job

**Data:**
* id: Id of the specific job	
### /Update/
**Description:**
Update a specific job with new field data

**Data**
* id: Id of the specific job to update
* job_name: Name of the job; Must be unique
* output_file: Name of the output file
* user: The user to whom the job belongs
* workspace: The workspace where the job belongs
* pce: The PCE on which the job will run
* module: The module for which the job will run
### /Delete/
**Description:**
Delete a specific job

**Data**
* id: Id of the specific job

---
# admin/PCEs

### /GetAll/
**Description:**
Retrieve all configured PCEs
		
### /Modules/
**Description:**
Retrieve all modules from a specific PCE

**Data**
* pce_id: Id of specific PCE
			
### /Module/Add/
**Description:**
Add a module to a specific PCE

**Data**
* module_name: Name of the module
* version: Version of the module
* src_location: Location of source code
* descripton: Descriptoin of module
* pce_id: Id of specific PCE on which to add the module
			
### /Module/Edit/
**Description:**
Edit a module

**Data**
* module_id: Id of specific module
* module_name: Name of the module
* version: Version of the module
* src_location: Location of source code
* descripton: Descriptoin of module
			
### /Module/Delete/
**Description:**
Delete a module

**Data**
* id: Id of module to delete
			
### /Module/State/
**Description:**
Retrieve state of a specific module on specific a PCE
			
**Data**
* module_id: Id for specific module
* pce_id: Id for specific PCE
			
### /Module/Deploy/
**Description:**
Deploy a specific module on a specific PCE
			
**Data**
* module_id: Id for specific module
* pce_id: Id for specific PCE
			
### /Add/
**Description:**
Add a new PCE

**Data**
* name: Name of PCE
* ip_addr: IP address of PCE
* ip_port: Port of PCE
* pce_username: Username for PCE
* contact_info: Your contact info
* description: Description for PCE
* location: Physical location of PCE
			
### /Edit/
**Description:**
Edit a specific PCE
			
**Data**
* pce_id: Id of specific PCE
* pce_name: Name of PCE
* ip_addr: IP address of PCE
* ip_port: Port of PCE
* pce_username: Username for PCE
* contact_info: Your contact info
* description: Description for PCE
* location: Physical location of PCE
			
### /Delete/
**Description:**
Delete a specific PCE
		
**Data**
* id: Id of specific PCE
			
### /Workspaces/
**Description:**
Retrieve all workspaces for a specific PCE

**Data**
* pce_id: Id for specific PCE
			
### /Jobs/
**Description:**
Retrieve all jobs for a specific PCE
			
**Data**
* pce_id: Id for specific PCE

---
# admin/Users

### /GetAll/
**Description:**
Retrieve all OnRamp users
		
### /Create/
**Description:**
Create a new user

**Data**
* first_name: First name of specific user
* last_name: Last name of specific user
* password: Encrypted password
* username: Username of specific user
* email: Email of specific user
* is_admin: Is the user an administrator; default=false
* is_enabled: Is the user enabled; default=false
			
### /Update/
**Description:**
Update a specific user

**Data**
* user_id: Id for specific user
* first_name: First name of specific user
* last_name: Last name of specific user
* password: Encrypted password
* username: Username of specific user
* email: Email of specific user
* is_admin: Is the user an administrator; default=false
* is_enabled: Is the user enabled; default=false
			
### /Disable/
**Description:**
Disable a specific enabled user
They will no longer be able to login
			
**Data**
* user_id: Id for specific user
			
### /Enable/
**Description:**
Enable a specific disabled user
They will be able to login again
	
**Data**
* user_id: Id for specific user
			
### /Delete/
**Description:**
Remove a specific user

**Data**
* user_id: Id for specific user
			
### /Jobs/
**Description:**
Retrieve all jobs run by a specific user

**Data**
* user_id: Id for specific user
			
### /Workspaces/
**Description:**
Retrieve all workspaces for a specific user

**Data**
* user_id: Id for specific user

---
# public/Dashboard

### /GetWorkspaces/
**Description:**
Retrieve all workspaces for the logged in user
		
### /GetJobs/
**Description:**
Retrieve all jobs for the logged in user

---
# public/Jobs

### /GetJobInfo/
**Description:**
Retrieve information for a specific job

**Data**
* job_id: Id of specific job
	
### /UserJobs/
**Description:**
Retrieve all jobs for the logged in user

---
# public/Workspace

### /GetWorkspace/
**Description:**
Retrieve information for a specific workspace

**Data**
* workspace_id: Id of specific workspace
			
### /GetPCEs/
**Description:**
Retrieve all PCEs for a specific workspace

**Data**
* workspace_id: Id of specific workspace
			
### /GetModules/
**Description:**
Retrieve installed modules based on workspace/pce combination

**Data**
* workspace_id: Id of specific workspace
* pce_id: Id of specific PCE
			
### /GetModuleOptions/
**Description:**
Retrieve options for a specific module

Data
* pce_id: Id of specific PCE
* module_id: Id of specific module
			
### /LaunchJob/
**Description:**
Launches a job

**Data**
* pce_id: Id of specific PCE
* module_id: Id of specific module
* workspace_id: Id of specific workspace
* job_name: The name of the job to launch
* ui_options: The options for the job
