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

	self.viewModule = function () {
		// go to manage users page and start with this user
		window.location.href = "admin_modules.html";
	};
}

function UserProfile(data) {
	var self = this;
	self.id = ko.observable(data['id']);
	self.username = ko.observable(data['username']);
	self.fullName = ko.observable(data['fullName']);
	self.email = ko.observable(data['email']);
	self.isAdmin = ko.observable(data['isAdmin']);

	self.Workspacelist = ko.observableArray();
	self.Jobslist = ko.observableArray();
	self.PCEslist = ko.observableArray();
	self.Moduleslist = ko.observableArray();

	self.viewUser = function () {
		// go to manage users page and start with this user
		window.location.href = "admin_users.html";
	};

	self.editUser = function () {
		// get all user data
		// start with some dummy data



		self.Jobslist.push(new Job({'JobID':1, 'User': 4, 'Workspace':1, 'PCE': 2, 'Module':1, 'RunName':'test1', 'Status':'Running', 'Runtime':'0:32'}));
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

		self.Workspacelist.push(new Workspace({'WorkspaceID': 1, 'WorkspaceName': 'default', 'Description':'My personal workspace'}));

		self.Moduleslist.push(new Module({'ID':1,
		'name':'Hello MPI',
		'details':'a first parallel program',
		'formFields':{
			'runname':'',
			'nodes':1,
			'tasks':4}}));
		};

		self.updateServer = function () {
			// create put call
			alert("updating user info on server");
		}

		self.removeFromWorkspace = function () {
			// this is the workspace object
			self.Workspacelist.remove(this);
			alert("removing " + self.username() + " from workspace " + this.name);
		}

		self.removeOnServer = function () {
			alert("removing " + self.username() + " from the server.");
		}

	}



	function AdminUserViewModel() {
		var self = this;
		self.username = sessionStorage['UserID'];
		self.userID = sessionStorage['UserID'];

		self.selectedUser = ko.observable();

		self.Userslist = ko.observableArray();

		self.changeUser = function () {
			self.selectedUser(null);
		};

		self.selectUser = function () {
			self.selectedUser(this);
			this.editUser();
		}

		self.deleteUser = function () {
			// tell server to delete this user
			self.Userslist.remove(this);
			if (self.selectedUser() == this) {
				self.selectedUser(null);
			}
			this.removeOnServer();
		}

		self.addUser = function () {
			// need to get user ID from the server, maybe not until data is populated?
			var newUser = new UserProfile({'id':-1, 'username': 'username', 'fullName' : 'fullName', 'email':'emai', 'isAdmin': false});
			self.Userslist.push(newUser);
			self.selectedUser(newUser);
		}

		$(document).ready( function () {
			// reinitialize values
			self.Userslist([]);

			// get data from server
			// some hard coded data for now...
			self.Userslist.push(new UserProfile({'id':1, 'username':'Matilda', 'fullName':'Matilda Mae', 'email':'mm29@gmail.com','isAdmin':false}));
			self.Userslist.push(new UserProfile({'id':2, 'username':'Batilda', 'fullName':'Batilda Bee', 'email':'bb29@gmail.com','isAdmin':true}));
			self.Userslist.push(new UserProfile({'id':3, 'username':'Gatilda', 'fullName':'Gatilda Goo', 'email':'gg29@gmail.com','isAdmin':false}));
			self.Userslist.push(new UserProfile({'id':4, 'username':'Katilda', 'fullName':'Katilda Kitty', 'email':'kk29@gmail.com','isAdmin':false}));
		});

	}

	// Activates knockout.js
	ko.applyBindings(new AdminUserViewModel());
