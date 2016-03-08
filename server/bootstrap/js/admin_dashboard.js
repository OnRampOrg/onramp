


function UserProfile(data) {
	var self = this;
	self.id = data['user_id'];
	self.username = data['username'];
	self.fullName = data['full_name'];
	self.email = data['email'];
	self.isAdmin = data['is_admin'];
	self.isEnabled = data['is_enabled'];


	self.viewUser = function () {
		// go to manage users page and start with this user
		window.location.href = "admin_users.html";
	};

}

function AdminDashboardViewModel() {
	var self = this;
	self.username = ko.observable();
	self.userID = sessionStorage['UserID'];
	self.auth_data = sessionStorage['auth_data'];

	self.Userslist = ko.observableArray();
	self.Workspacelist = ko.observableArray();
	self.Jobslist = ko.observableArray();
	self.PCEslist = ko.observableArray();
	self.Moduleslist = ko.observableArray();


	//this.Jobslist.add(new Job({'JobID' : 2, 'Workspace' : 'default', 'PCE' : 'flux', 'Module' : 'Hello World', 'RunName' : 'test1', 'Status' : 'Running', 'Runtime' : '0:00'}));
	//this.Workspacelist.add(new Workspace({'WorkspaceID': 1, 'WorkspaceName': 'default', 'Description':'My personal workspace'}));
	//this.Workspacelist.add(new Workspace({'WorkspaceID': 2, 'WorkspaceName': 'test', 'Description':'testing workspace'}));

	self.welcome =   "Admin Panel: " + self.username();

	self.manageUsers = function () {
		window.location.href = "admin_users.html";
	};

	self.manageJobs = function () {
		window.location.href = "admin_jobs.html";
	};

	self.manageWorkspaces = function () {
		window.location.href = "admin_workspaces.html";
	};

	self.managePCEs = function () {
		window.location.href = "admin_PCEs.html";
	};

	self.manageModules = function () {
		window.location.href = "admin_Modules.html";
	};

	$(document).ready( function () {
		// reinitialize values
		self.Userslist([]);
		self.Workspacelist([]);
		self.Jobslist([]);
		self.PCEslist([]);
		self.Moduleslist([]);



		// get data from server
		$.getJSON( "http://flux.cs.uwlax.edu/onramp/api/users/" + self.userID + "?apikey=" + JSON.parse(self.auth_data).apikey,
					function (data){
					// {"status": 0,
					//  "status_message": "Success",
					//  "users": {
					//    "fields": ["user_id", "username", "full_name", "email", "is_admin", "is_enabled"],
					//    "data": [2, "alice", "", "", 0, 1]}}
					console.log(data);
					self.username(data.users.data[1]);
					sessionStorage['UserName'] = self.username();
				}
		);

		$.getJSON( "http://flux.cs.uwlax.edu/onramp/api/users?apikey=" + JSON.parse(self.auth_data).apikey,
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
							self.Userslist.push(new UserProfile(conv_data));
						}
					}
		);


		$.getJSON( "http://flux.cs.uwlax.edu/onramp/api/jobs?apikey=" + JSON.parse(self.auth_data).apikey,
								//self.auth_data,
								function (data){
									// {"status": 0,
									//  "status_message": "Success",
									//  "users": {
									//    "fields": ["user_id", "username", "full_name", "email", "is_admin", "is_enabled"],
									//    "data": [2, "alice", "", "", 0, 1]}}
									console.log(JSON.stringify(data));
									for (var x = 0; x < data.jobs.data.length; x++){
										var raw = data.jobs.data[x];
										console.log(raw);
										var conv_data = {};
										for(var i = 0; i < data.jobs.fields.length; i++){
											console.log("adding: " + data.jobs.fields[i] + " = " + raw[i]);
											conv_data[data.jobs.fields[i]] = raw[i];
										}
										self.Jobslist.push(new Job(conv_data, true, false));
									}
								}
							);

		// get workspaces for this user
		$.getJSON( "http://flux.cs.uwlax.edu/onramp/api/workspaces?apikey=" + JSON.parse(self.auth_data).apikey,
								//self.auth_data,
								function (data){
									// {"status": 0,
									//  "status_message": "Success",
									//  "users": {
									//    "fields": ["user_id", "username", "full_name", "email", "is_admin", "is_enabled"],
									//    "data": [2, "alice", "", "", 0, 1]}}
									console.log(JSON.stringify(data));
									for (var x = 0; x < data.workspaces.data.length; x++){
										var raw = data.workspaces.data[x];
										console.log(raw);
										var conv_data = {};
										for(var i = 0; i < data.workspaces.fields.length; i++){
											console.log("adding: " + data.workspaces.fields[i] + " = " + raw[i]);
											conv_data[data.workspaces.fields[i]] = raw[i];
										}
										self.Workspacelist.push(new Workspace(conv_data, true));
									}
								}
							);

		$.getJSON( "http://flux.cs.uwlax.edu/onramp/api/pces?apikey=" + JSON.parse(self.auth_data).apikey,
								//self.auth_data,
								function (data){
									// {"status": 0,
									//  "status_message": "Success",
									//  "users": {
									//    "fields": ["user_id", "username", "full_name", "email", "is_admin", "is_enabled"],
									//    "data": [2, "alice", "", "", 0, 1]}}
									console.log(JSON.stringify(data));
									for (var x = 0; x < data.pces.data.length; x++){
										var raw = data.pces.data[x];
										console.log(raw);
										var conv_data = {};
										for(var i = 0; i < data.pces.fields.length; i++){
											console.log("adding: " + data.pces.fields[i] + " = " + raw[i]);
											conv_data[data.pces.fields[i]] = raw[i];
										}
										self.PCEslist.push(new PCE(conv_data, true));
									}
								}
							);

		$.getJSON( "http://flux.cs.uwlax.edu/onramp/api/modules?apikey=" + JSON.parse(self.auth_data).apikey,
								//self.auth_data,
								function (data){
									// {"status": 0,
									//  "status_message": "Success",
									//  "users": {
									//    "fields": ["user_id", "username", "full_name", "email", "is_admin", "is_enabled"],
									//    "data": [2, "alice", "", "", 0, 1]}}
									console.log(JSON.stringify(data));
									for (var x = 0; x < data.modules.data.length; x++){
										var raw = data.modules.data[x];
										console.log(raw);
										var conv_data = {};
										for(var i = 0; i < data.modules.fields.length; i++){
											console.log("adding: " + data.modules.fields[i] + " = " + raw[i]);
											conv_data[data.modules.fields[i]] = raw[i];
										}
										self.Moduleslist.push(new Module(conv_data, true));
									}
								}
							);
		});


	}

	// Activates knockout.js
	ko.applyBindings(new AdminDashboardViewModel());
