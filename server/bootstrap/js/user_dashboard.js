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
	

	this.captureWSID = function () {
		sessionStorage.setItem("WorkspaceID", this.wID);
		//alert("workspace " + localStorage.getItem('WorkspaceID'));
		window.location.href = "workspace.html";
	}
	
}


function UserDashboardViewModel() {
	var self = this;
	self.username = sessionStorage['UserID'];  // want to get this from the cookie/session/server
	self.userID = sessionStorage['UserID'];
	self.Workspacelist = ko.observableArray([new Workspace({'WorkspaceID': 1, 'WorkspaceName': 'default', 'Description':'My personal workspace'}), new Workspace({'WorkspaceID': 2, 'WorkspaceName': 'test', 'Description':'Hello world'})]);  // want to get this from the server
	self.Jobslist = ko.observableArray([new Job({'JobID' : 2, 'Workspace' : 'default', 'PCE' : 'flux', 'Module' : 'Hello World', 'RunName' : 'test1', 'Status' : 'Running', 'Runtime' : '0:00'})]);
	
	//this.Jobslist.add(new Job({'JobID' : 2, 'Workspace' : 'default', 'PCE' : 'flux', 'Module' : 'Hello World', 'RunName' : 'test1', 'Status' : 'Running', 'Runtime' : '0:00'}));
	//this.Workspacelist.add(new Workspace({'WorkspaceID': 1, 'WorkspaceName': 'default', 'Description':'My personal workspace'}));
	//this.Workspacelist.add(new Workspace({'WorkspaceID': 2, 'WorkspaceName': 'test', 'Description':'testing workspace'}));
	
	self.welcome =   "Welcome " + self.username;
	
	self.getDataFromServer = function () {
		// get all the data we need from the server
		
		// replace with something like (not inside a function):
		//
		// Load initial state from server, convert it to Task instances, then populate self.tasks
		//$.getJSON("/tasks", function(allData) {
        //var mappedTasks = $.map(allData, function(item) { return new Task(item) });
        //self.tasks(mappedTasks);
		//});
		
		// some dummy data for testing:
		self.Jobslist.push(new Job({'JobID' : 2, 'Workspace' : 'default', 'PCE' : 'flux', 'Module' : 'Hello World', 'RunName' : 'test1', 'Status' : 'Running', 'Runtime' : '0:00'}));
		self.Workspacelist.push(new Workspace({'WorkspaceID': 1, 'WorkspaceName': 'default', 'Description':'My personal workspace'}));
		self.Workspacelist.push(new Workspace({'WorkspaceID': 2, 'WorkspaceName': 'test', 'Description':'testing workspace'}));
	}
	
	

	
	self.showAllJobs = function (){
		// show the list of all jobs
	}
	
	self.viewJobDetails = function () {
		// show details of job on same page
	}
	
	
}

// Activates knockout.js
ko.applyBindings(new UserDashboardViewModel());