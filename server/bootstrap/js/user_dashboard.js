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

	self.gotoJobDetails = function () {
		window.location.href = "job_details.html";
	}
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
	self.userID = sessionStorage['UserID'];
	self.auth_data = sessionStorage['auth_data'];
	self.Workspacelist = ko.observableArray();
	self.Jobslist = ko.observableArray();

	self.username = JSON.parse(self.auth_data).username;
	self.welcome = "Welcome " + self.username;

	//this.Jobslist.add(new Job({'JobID' : 2, 'Workspace' : 'default', 'PCE' : 'flux', 'Module' : 'Hello World', 'RunName' : 'test1', 'Status' : 'Running', 'Runtime' : '0:00'}));
	//this.Workspacelist.add(new Workspace({'WorkspaceID': 1, 'WorkspaceName': 'default', 'Description':'My personal workspace'}));
	//this.Workspacelist.add(new Workspace({'WorkspaceID': 2, 'WorkspaceName': 'test', 'Description':'testing workspace'}));



	$(document).ready( function () {
		console.log(self.auth_data);
		console.log(JSON.stringify(self.auth_data));
		console.log(JSON.parse(self.auth_data).username);

		// get jobs for this user
		$.getJSON( sessionStorage.server + "/users/" + self.userID + "/jobs?apikey=" + JSON.parse(self.auth_data).apikey,
								//self.auth_data,
								function (data){
									// {"status": 0,
									//  "status_message": "Success",
									//  "users": {
									//    "fields": ["user_id", "username", "full_name", "email", "is_admin", "is_enabled"],
									//    "data": [2, "alice", "", "", 0, 1]}}
									console.log(JSON.stringify(data));
									for (var x = 0; x < data.users.data.length; x++){
										var raw = data.users.data[x];
										console.log(raw);
										var conv_data = {};
										for(var i = 0; i < data.users.fields.length; i++){
											console.log("adding: " + data.users.fields[i] + " = " + raw[i]);
											conv_data[data.users.fields[i]] = raw[i];
										}
										self.Jobslist.push(new Job(conv_data));
									}
								}
							);

		// get workspaces for this user
		$.getJSON( sessionStorage.server + "/users/" + self.userID + "/workspaces?apikey=" + JSON.parse(self.auth_data).apikey,
								//self.auth_data,
								function (data){
									// {"status": 0,
									//  "status_message": "Success",
									//  "users": {
									//    "fields": ["user_id", "username", "full_name", "email", "is_admin", "is_enabled"],
									//    "data": [2, "alice", "", "", 0, 1]}}
									console.log(JSON.stringify(data));
									for (var x = 0; x < data.users.data.length; x++){
										var raw = data.users.data[x];
										console.log(raw);
										var conv_data = {};
										for(var i = 0; i < data.users.fields.length; i++){
											console.log("adding: " + data.users.fields[i] + " = " + raw[i]);
											conv_data[data.users.fields[i]] = raw[i];
										}
										self.Workspacelist.push(new Workspace(conv_data));
									}
								}
							);

		// some dummy data for testing:
		//self.Jobslist.push(new Job({'JobID' : 2, 'Workspace' : 'default', 'PCE' : 'flux', 'Module' : 'Hello World', 'RunName' : 'test1', 'Status' : 'Running', 'Runtime' : '0:00'}));
		//self.Workspacelist.push(new Workspace({'WorkspaceID': 1, 'WorkspaceName': 'default', 'Description':'My personal workspace'}));
		//self.Workspacelist.push(new Workspace({'WorkspaceID': 2, 'WorkspaceName': 'test', 'Description':'testing workspace'}));
	});



	self.logout = function (){
		// send post to server
		$.ajax({
		  type: 'POST',
		  url: sessionStorage.server + '/logout',
		  data: self.auth_data,
		  complete: function () {
			  window.location.href = "start.html";
		  },
		  dataType: 'application/json',
		  contentType: 'application/json'
		} );

	}



}

// Activates knockout.js
ko.applyBindings(new UserDashboardViewModel());
