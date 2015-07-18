function Job(data){
	var self = this;
	self.jID = data['JobID'];
	self.ws = data['Workspace'];
	self.pce = data['PCE'];
	self.mod = data['Module'];
	self.name = data['RunName'];
	self.status = data['Status'];
	self.time = data['Runtime'];
}

function Workspace(data){
	var self = this;
	self.wID = data['WorkspaceID'];
	self.name = data['WorkspaceName'];
	self.desc = data['Description'];
}

function UserDashboardViewModel() {
	this.username = localStorage['UserID'];  // want to get this from the cookie/session/server
	this.userID = localStorage['UserID'];
	this.Workspacelist = ko.observableArray([new Workspace({'WorkspaceID': 1, 'WorkspaceName': 'default', 'Description':'My personal workspace'}), new Workspace({'WorkspaceID': 2, 'WorkspaceName': 'test', 'Description':'Hello world'})]);  // want to get this from the server
	this.Jobslist = ko.observableArray([new Job({'JobID' : 2, 'Workspace' : 'default', 'PCE' : 'flux', 'Module' : 'Hello World', 'RunName' : 'test1', 'Status' : 'Running', 'Runtime' : '0:00'})]);
	
	//this.Jobslist.add(new Job({'JobID' : 2, 'Workspace' : 'default', 'PCE' : 'flux', 'Module' : 'Hello World', 'RunName' : 'test1', 'Status' : 'Running', 'Runtime' : '0:00'}));
	//this.Workspacelist.add(new Workspace({'WorkspaceID': 1, 'WorkspaceName': 'default', 'Description':'My personal workspace'}));
	//this.Workspacelist.add(new Workspace({'WorkspaceID': 2, 'WorkspaceName': 'test', 'Description':'testing workspace'}));
	
	this.welcome =   "Welcome " + this.username;
	
	this.getDataFromServer = function () {
		// get all the data we need from the server
		// some dummy data for testing:
		this.Jobslist.add(new Job({'JobID' : 2, 'Workspace' : 'default', 'PCE' : 'flux', 'Module' : 'Hello World', 'RunName' : 'test1', 'Status' : 'Running', 'Runtime' : '0:00'}));
		this.Workspacelist.add(new Workspace({'WorkspaceID': 1, 'WorkspaceName': 'default', 'Description':'My personal workspace'}));
		this.Workspacelist.add(new Workspace({'WorkspaceID': 2, 'WorkspaceName': 'test', 'Description':'testing workspace'}));
	}
	
	
	
	this.showAllJobs = function (){
		// show the list of all jobs
	}
	
	this.viewJobDetails = function () {
		// show details of job on same page
	}
}

// Activates knockout.js
ko.applyBindings(new UserDashboardViewModel());