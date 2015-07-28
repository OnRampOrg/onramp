function Job(data){
	var self = this;
	self.jID = data['job_id'];
	self.user = data['user_id'];
	self.ws = data['workspace_id'];
	self.pce = data['pce_id'];
	self.mod = data['module_id'];
	self.name = data['job_name'];
	self.status = data['state'];
	self.time = "0:00";  // not implemented yet
}

function Workspace(data){
	var self = this;
	self.wID = data['workspace_id'];
	self.name = data['workspace_name'];
	self.desc = data['description'];


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
	self.auth_data = sessionStorage['auth_data'];
	self.Workspacelist = ko.observableArray([new Workspace({'WorkspaceID': 1, 'WorkspaceName': 'default', 'Description':'My personal workspace'}), new Workspace({'WorkspaceID': 2, 'WorkspaceName': 'test', 'Description':'Hello world'})]);  // want to get this from the server
	self.Jobslist = ko.observableArray([new Job({'JobID' : 2, 'Workspace' : 'default', 'PCE' : 'flux', 'Module' : 'Hello World', 'RunName' : 'test1', 'Status' : 'Running', 'Runtime' : '0:00'})]);

	//this.Jobslist.add(new Job({'JobID' : 2, 'Workspace' : 'default', 'PCE' : 'flux', 'Module' : 'Hello World', 'RunName' : 'test1', 'Status' : 'Running', 'Runtime' : '0:00'}));
	//this.Workspacelist.add(new Workspace({'WorkspaceID': 1, 'WorkspaceName': 'default', 'Description':'My personal workspace'}));
	//this.Workspacelist.add(new Workspace({'WorkspaceID': 2, 'WorkspaceName': 'test', 'Description':'testing workspace'}));

	self.welcome =   "Welcome " + self.username;

	$(document).ready( function () {
		console.log(self.auth_data);
		console.log(JSON.stringify(self.auth_data));
		$.getJSON( "http://flux.cs.uwlax.edu/onramp/api/users/" + self.userID + "?apikey=" + JSON.parse(self.auth_data).apikey,
								self.auth_data,
								function (data){
									// {"status": 0,
									//  "status_message": "Success",
									//  "users": {
									//    "fields": ["user_id", "username", "full_name", "email", "is_admin", "is_enabled"],
									//    "data": [2, "alice", "", "", 0, 1]}}
									console.log(data);
									self.username(data.users.data[1]);
								}
							);

		// get jobs for this user
		$.getJSON( "http://flux.cs.uwlax.edu/onramp/api/users/" + self.userID + "/jobs?apikey=" + JSON.parse(self.auth_data).apikey,
								self.auth_data,
								function (data){
									// {"status": 0,
									//  "status_message": "Success",
									//  "users": {
									//    "fields": ["user_id", "username", "full_name", "email", "is_admin", "is_enabled"],
									//    "data": [2, "alice", "", "", 0, 1]}}
									console.log(data);
									for (raw in data.users.data){
										var conv_data = {};
										for(var i = 0; i < data.users.fields.length; i++){
											conv_data[data.users.fields[i]] = raw[i];
										}
										self.JobsList.push(new Job(conv_data));
									}
								}
							);

		// get workspaces for this user


		// some dummy data for testing:
		//self.Jobslist.push(new Job({'JobID' : 2, 'Workspace' : 'default', 'PCE' : 'flux', 'Module' : 'Hello World', 'RunName' : 'test1', 'Status' : 'Running', 'Runtime' : '0:00'}));
		self.Workspacelist.push(new Workspace({'WorkspaceID': 1, 'WorkspaceName': 'default', 'Description':'My personal workspace'}));
		self.Workspacelist.push(new Workspace({'WorkspaceID': 2, 'WorkspaceName': 'test', 'Description':'testing workspace'}));
	});






}

// Activates knockout.js
ko.applyBindings(new UserDashboardViewModel());
