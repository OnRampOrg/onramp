function Job(data){
	var self = this;
	self.jID = data['JobID'];
	self.user = data['User'];
	self.ws = data['Workspace'];
	self.pce = data['PCE'];
	self.mod = data['Module'];
	self.name = data['RunName'];
	self.status = data['Status'];
	self.time = data['Runtime'];
	
	self.viewJob = function () {
		// go to manage Jobs page and show this job
		window.location.href = "admin_jobs.html";
	}
}

function PCE (data) {
	var self = this;
	
	self.ID = data['ID'];
	self.name = data['name'];
	self.status = data['status'];
	self.nodes = data['nodes'];
	self.corespernode = data['corespernode'];
	self.mempernode = data['mempernode'];
	self.description = data['description'];
	
	self.viewPCE = function () {
		// go to manage Workspaces page and show this job
		window.location.href = "admin_PCEs.html";
	}
}

function Workspace(data){
	var self = this;
	self.wID = data['WorkspaceID'];
	self.name = data['WorkspaceName'];
	self.desc = data['Description'];
	
	self.viewWorkspace = function () {
		// go to manage Workspaces page and show this job
		window.location.href = "admin_workspaces.html";
	}
	
	this.captureWSID = function () {
		sessionStorage.setItem("WorkspaceID", this.wID);
		//alert("workspace " + localStorage.getItem('WorkspaceID'));
		window.location.href = "workspace.html";
	}
	
}

function Module(data){
	var self = this;
	self.mID = data['ID'];
	self.name = data['name'];
	self.desc = data['details'];
	self.formFields = ko.observableArray();
	for(k in data['formFields']){
		self.formFields.push([k, data['formFields'][k]]);
	}
	
	self.viewUser = function () {
		// go to manage users page and start with this user
		window.location.href = "admin_modules.html";
	};
}

function UserProfile(data) {
	var self = this;
	self.id = data['id'];
	self.username = data['username'];
	self.fullName = data['fullName'];
	self.isAdmin = data['isAdmin'];
	
	self.viewUser = function () {
		// go to manage users page and start with this user
		window.location.href = "admin_users.html";
	};
	
}

function AdminDashboardViewModel() {
	var self = this;
	self.username = sessionStorage['UserID'];  
	self.userID = sessionStorage['UserID'];
	
	self.Userslist = ko.observableArray();
	self.Workspacelist = ko.observableArray();  
	self.Jobslist = ko.observableArray();
	self.PCEslist = ko.observableArray();  
	self.Moduleslist = ko.observableArray();

	
	//this.Jobslist.add(new Job({'JobID' : 2, 'Workspace' : 'default', 'PCE' : 'flux', 'Module' : 'Hello World', 'RunName' : 'test1', 'Status' : 'Running', 'Runtime' : '0:00'}));
	//this.Workspacelist.add(new Workspace({'WorkspaceID': 1, 'WorkspaceName': 'default', 'Description':'My personal workspace'}));
	//this.Workspacelist.add(new Workspace({'WorkspaceID': 2, 'WorkspaceName': 'test', 'Description':'testing workspace'}));
	
	self.welcome =   "Admin Panel: " + self.username;
	
	self.manageUsers = function () {
		window.location.href = "admin_users.html";
	}
	
	self.manageJobs = function () {
		window.location.href = "admin_jobs.html";
	}
	
	self.manageWorkspaces = function () {
		window.location.href = "admin_workspaces.html";
	}

	self.managePCEs = function () {
		window.location.href = "admin_PCEs.html";
	}
	
	self.manageModules = function () {
		window.location.href = "admin_Modules.html";
	}
	
	$(document).ready( function () {
		// reinitialize values
		self.Userslist([]);
		self.Workspacelist([]); 
		self.Jobslist([]);
		
		// get data from server
					// some hard coded data for now...
		self.Userslist.push(new UserProfile({'id':1, 'username':'Matilda', 'fullName':'Matilda Mae', 'isAdmin':false}));
		self.Userslist.push(new UserProfile({'id':2, 'username':'Batilda', 'fullName':'Batilda Bee', 'isAdmin':true}));
		self.Userslist.push(new UserProfile({'id':3, 'username':'Gatilda', 'fullName':'Gatilda Goo', 'isAdmin':false}));
		self.Userslist.push(new UserProfile({'id':4, 'username':'Katilda', 'fullName':'Katilda Kitty', 'isAdmin':false}));
			
		self.Jobslist.push(new Job({'JobID':1, 'User': 4, 'Workspace':1, 'PCE': 2, 'Module':1, 'RunName':'test1', 'Status':'Running', 'Runtime':'0:32'}));
		self.Jobslist.push(new Job({'JobID':2, 'User': 4, 'Workspace':1, 'PCE': 1, 'Module':1, 'RunName':'test2', 'Status':'Running', 'Runtime':'0:02'}));
		self.Jobslist.push(new Job({'JobID':3, 'User': 4, 'Workspace':1, 'PCE': 2, 'Module':2, 'RunName':'does it work?', 'Status':'Queued', 'Runtime':'--'}));
		
		self.Workspacelist.push(new Workspace({'WorkspaceID': 1, 'WorkspaceName': 'default', 'Description':'My personal workspace'}));
		self.Workspacelist.push(new Workspace({'WorkspaceID': 2, 'WorkspaceName': 'test', 'Description':'testing workspace'}));
			
		// get PCE list
		self.PCEslist.push(new PCE({'ID': 1,
								   'name': 'flux',
								   'description':'cluster',
								   'status':'up',
								   'nodes':4,
								   'corespernode':16,
								   'mempernode':'8GB'}));
				
		self.PCEslist.push(new PCE({'ID': 1,
								   'name': 'brie',
								   'description':'LittleFe',
								   'status':'up',
								   'nodes':6,
								   'corespernode':2,
								   'mempernode':'1GB'}));
			
		self.PCEslist.push(new PCE({'ID': 3,
								   'name': 'gouda',
								   'description':'LittleFe',
								   'status':'up',
								   'nodes':6,
								   'corespernode':2,
								   'mempernode':'0.5GB'}));
		
		// get module list
		self.Moduleslist.push(new Module({'ID':1,
										 'name':'Hello MPI',
										 'details':'a first parallel program',
										 'formFields':{
											'runname':'',
											'nodes':1,
											'tasks':4}}));
		});
		
}

// Activates knockout.js
ko.applyBindings(new AdminDashboardViewModel());